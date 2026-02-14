from fastapi import FastAPI, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from uvicorn import run
from core import logger
from schema.relectionSchema import Reflection
from model.result import Result
from schema.userSchema import UserRequest, UserRes
from core.container import db_container
from schema.questionSchema import QuestionTraitCreate
from schema.aggreSchema import AggregationRequest
from schema.aggreSchema import AggregationResponse
from schema.sessionSchema import SessionRequest, SessionRes, SessionRenameRequest, SessionDeleteRequest
from schema.chatSchema import ChatListRes, ChatRequest

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
def create_questions(question: QuestionTraitCreate):
    logger.info('添加问题')
    if db_container.question_service.create_question(question) is not None:
        logger.info('问题添加成功')
        return Result.success("成功添加！")
    else:
        logger.info('问题添加失败')
        return Result.fail("添加失败", -1)


@app.get('/generateQuestions/{number}')
def generate_questions(number: int):
    logger.info(f'agent生成{number}个问题')
    result = db_container.question_service.generate_questions(number)
    if result == number:
        logger.info('问题生成成功')
        return Result.success("全部问题成功添加！")
    else:
        logger.info('问题生成失败')
        return Result.fail(f"{number - result}个问题添加失败", -1)


@app.get('/getQuestions/{number}')
def get_questions(number: int):
    logger.info(f'获取{number}个问题')
    result = db_container.question_service.get_questions(number)
    if len(result) == number:
        logger.info('获取全部问题')
    else:
        logger.info(f'获取{number - len(result)}个问题')
    return Result.success(data=result)


@app.post('/reflection')
async def reflection(dto: Reflection, background_tasks: BackgroundTasks):
    logger.info(f'收到分析请求：{dto}')
    background_tasks.add_task(db_container.reflection_service.get_reflection, dto)
    return Result.success("已提交分析任务")


@app.post('/aggregation')
def aggregation(dto: AggregationRequest):
    logger.info(f'总结用户{dto.user}的全部测试结果')
    db_container.agg_service.generate_aggregate(dto.user)
    logger.info(f'成功存储更新结果')
    return Result.success()


@app.post('/getAggregation')
def get_aggregation(dto: AggregationRequest):
    logger.info(f'获取用户{dto.user}的aggregation')
    aggregate = db_container.agg_service.get_aggregate(dto.user)
    logger.info(f'成功获取')
    return Result.success(data=AggregationResponse.from_orm(aggregate))


@app.post('/getSessions', response_model=Result[list[SessionRes]])
def get_sessions(dto: SessionRequest):
    logger.info(f'获取用户{dto.user}的Session')
    sessions = db_container.session_service.get_sessions(dto.user)
    logger.info(f'成功获取')
    return Result.success(data=sessions)


@app.post('/createSession')
def create_session(dto: SessionRequest):
    logger.info(f'为用户{dto.user}创建新Session，初始问题：{dto.message}')
    session = db_container.session_service.create_session(dto.user, dto.message)
    logger.info(f'成功创建Session: {session.id}')
    return Result.success(data=session.id)


@app.post('/renameSession')
def rename_session(dto: SessionRenameRequest):
    logger.info(f'重命名Session {dto.session_id} 为 {dto.title}')
    session = db_container.session_service.rename_session(dto.session_id, dto.title)
    if session:
        return Result.success("重命名成功")
    return Result.fail("重命名失败")


@app.post('/deleteSession')
def delete_session(dto: SessionDeleteRequest):
    logger.info(f'删除Session {dto.session_id}')
    success = db_container.session_service.delete_session(dto.session_id)
    if success:
        return Result.success("删除成功")
    return Result.fail("删除失败")


@app.post('/generateUserTags')
async def generate_tags(dto: UserRequest, background_tasks: BackgroundTasks):
    logger.info(f'收到分析请求：生成{dto.user}对应的tags')
    background_tasks.add_task(db_container.user_service.generate_tag, dto.user)
    return Result.success("请求已经成功发出")


@app.post('/getUser', response_model=Result[UserRes])
def get_user(dto: UserRequest):
    logger.info(f'获取用户{dto.user}的信息')
    user = db_container.user_service.get_user(dto.user)
    if user:
        return Result.success(data=UserRes.from_orm(user))
    return Result.fail("用户不存在")


@app.get('/getChats/{session_id}', response_model=Result[ChatListRes])
def get_chats(session_id: int):
    logger.info(f'获取{session_id}对应的chats')
    chats = db_container.chat_service.get_chats(session_id)
    logger.info(f'成功获取')
    result = ChatListRes(
        chats=chats,
        session_id=session_id
    )
    return Result.success(data=result)


@app.post('/chat')
def chat(dto: ChatRequest):
    logger.info(f'用户{dto.user},session_id={dto.session_id},发来对话')
    ans = db_container.chat_service.generate_chat(dto.user, dto.session_id, dto.message)
    logger.info("成功回复")
    db_container.chat_service.save_chat(dto.session_id, 0, dto.message)
    db_container.chat_service.save_chat(dto.session_id, 1, ans)
    logger.info("成功存储请求和ai返回")
    return Result.success(data=ans)


if __name__ == '__main__':
    run("api.PeopleScopeApi:app", host='127.0.0.1', port=8080, reload=True)
