from fastapi import FastAPI, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from uvicorn import run
from core import logger
from schema.relectionSchema import Reflection
from model.result import Result
from schema.userSchema import UserRequest, UserRes
from service.ChatService import ChatService
from service.ReflectionService import ReflectionService
from service.QuestionService import QuestionService
from service.AggregationService import AggregationService
from fastapi import Depends
from sqlalchemy.orm import Session
from core.container import db_container
from schema.questionSchema import QuestionTraitCreate
from schema.aggreSchema import AggregationRequest
from schema.aggreSchema import AggregationResponse
from schema.sessionSchema import SessionRequest, SessionRes, SessionRenameRequest, SessionDeleteRequest
from service.SessionService import SessionService
from schema.chatSchema import ChatListRes,ChatRequest
from service.UserService import UserService

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 开发阶段直接放行
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger = logger.setup_logger()


@app.get('/')
def read_root():
    logger.info('测试连接成功，收到请求！')
    return {"Hello": "World"}


@app.post('/addQuestion')
def create_questions(question: QuestionTraitCreate, db: Session = Depends(db_container.get_mysql_db)):
    logger.info('添加问题')
    if QuestionService.create_question(db, question) is not None:
        logger.info('问题添加成功')
        return Result.success("成功添加！")
    else:
        logger.info('问题添加失败')
        return Result.fail("添加失败", -1)


@app.get('/generateQuestions/{number}')
def generate_questions(number: int, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'agent生成{number}个问题')
    result = QuestionService.generate_questions(db, number)
    if result == number:
        logger.info('问题生成成功')
        return Result.success("全部问题成功添加！")
    else:
        logger.info('问题生成失败')
        return Result.fail(f"{number - result}个问题添加失败", -1)


@app.get('/getQuestions/{number}')
def get_questions(number: int, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'获取{number}个问题')
    result = QuestionService.get_questions(db, number)
    if len(result) == number:
        logger.info('获取全部问题')
    else:
        logger.info(f'获取{number - len(result)}个问题')
    return Result.success(data=result)


@app.post('/reflection')
async def reflection(dto: Reflection, background_tasks: BackgroundTasks, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'收到分析请求：{dto}')
    background_tasks.add_task(ReflectionService.get_reflection, db, dto)
    return Result.success("已提交分析任务")


@app.post('/aggregation')
def aggregation(dto: AggregationRequest, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'总结用户{dto.user}的全部测试结果')
    AggregationService.generate_aggregate(db, dto.user)
    logger.info(f'成功存储更新结果')
    return Result.success()


@app.post('/getAggregation')
def get_aggregation(dto: AggregationRequest, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'获取用户{dto.user}的aggregation')
    aggregate = AggregationService.get_aggregate(db, dto.user)
    logger.info(f'成功获取')
    return Result.success(data=AggregationResponse.from_orm(aggregate))


@app.post('/getSessions', response_model=Result[list[SessionRes]])
def get_sessions(dto: SessionRequest, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'获取用户{dto.user}的Session')
    sessions = SessionService.get_sessions(db, dto.user)
    logger.info(f'成功获取')
    return Result.success(data=sessions)


@app.post('/createSession')
def create_session(dto: SessionRequest, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'为用户{dto.user}创建新Session，初始问题：{dto.message}')
    session = SessionService.create_session(db, dto.user, dto.message)
    logger.info(f'成功创建Session: {session.id}')
    return Result.success(data=session.id)


@app.post('/renameSession')
def rename_session(dto: SessionRenameRequest, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'重命名Session {dto.session_id} 为 {dto.title}')
    session = SessionService.rename_session(db, dto.session_id, dto.title)
    if session:
        return Result.success("重命名成功")
    return Result.fail("重命名失败")


@app.post('/deleteSession')
def delete_session(dto: SessionDeleteRequest, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'删除Session {dto.session_id}')
    success = SessionService.delete_session(db, dto.session_id)
    if success:
        return Result.success("删除成功")
    return Result.fail("删除失败")



@app.post('/generateUserTags')
async def generate_tags(dto: UserRequest, background_tasks: BackgroundTasks, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'收到分析请求：生成{dto.user}对应的tags')
    background_tasks.add_task(UserService.generate_tag(db, dto.user))
    return Result.success("请求已经成功发出")


@app.post('/getUser', response_model=Result[UserRes])
def get_user(dto: UserRequest, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'获取用户{dto.user}的信息')
    user = UserService.get_user(db, dto.user)
    if user:
        return Result.success(data=UserRes.from_orm(user))
    return Result.fail("用户不存在")


@app.get('/getChats/{session_id}', response_model=Result[ChatListRes])
def get_chats(session_id: int, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'获取{session_id}对应的chats')
    chats = ChatService.get_chats(db, session_id)
    logger.info(f'成功获取')
    result = ChatListRes(
        chats=chats,
        session_id=session_id
    )
    return Result.success(data=result)

@app.post('/chat')
def chat(dto: ChatRequest, db: Session = Depends(db_container.get_mysql_db)):
    logger.info(f'用户{dto.user},session_id={dto.session_id},发来对话')
    ans = ChatService.generate_chat(db, dto.user, dto.session_id, dto.message)
    logger.info("成功回复")
    ChatService.save_chat(db, dto.session_id, 0, dto.message)
    ChatService.save_chat(db, dto.session_id, 1, ans)
    logger.info("成功存储请求和ai返回")
    return Result.success(data=ans)


if __name__ == '__main__':
    run("api.PeopleScopeApi:app", host='127.0.0.1', port=8080, reload=True)
