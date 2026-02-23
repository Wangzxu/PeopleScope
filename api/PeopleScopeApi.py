from fastapi import FastAPI, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from core.logger import get_logger
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
logger = get_logger(__name__)


@app.get('/')
def read_root():
    logger.info("健康检查：服务连接正常，已接收请求。")
    return {"Hello": "World"}


@app.post('/addQuestion')
def create_questions(question: QuestionTraitCreate):
    logger.info("执行添加测评问题任务。")
    if db_container.question_service.create_question(question) is not None:
        logger.info("测评问题已成功持久化。")
        return Result.success("成功添加！")
    else:
        logger.error("测评问题持久化失败。")
        return Result.fail("添加失败", -1)


@app.get('/generateQuestions/{number}')
def generate_questions(number: int):
    logger.info(f"触发 Agent 自动生成任务：请求生成 {number} 个测评问题。")
    result = db_container.question_service.generate_questions(number)
    if result == number:
        logger.info(f"测评问题生成并添加成功，共计 {number} 个。")
        return Result.success("全部问题成功添加！")
    else:
        logger.warning(f"测评问题生成任务部分失败：预期 {number} 个，实际完成 {result} 个。")
        return Result.fail(f"{number - result}个问题添加失败", -1)


@app.get('/getQuestions/{number}')
def get_questions(number: int):
    logger.info(f"请求检索测评问题，目标数量：{number}。")
    result = db_container.question_service.get_questions(number)
    if len(result) == number:
        logger.info(f"成功检索全部请求的测评问题（{number} 个）。")
    else:
        logger.info(f"测评问题检索完成，实际获取数量：{len(result)}（请求数量：{number}）。")
    return Result.success(data=result)


@app.post('/reflection')
async def reflection(dto: Reflection, background_tasks: BackgroundTasks):
    logger.info(f"接收到用户分析请求（Reflection），用户ID: {dto.user}")
    background_tasks.add_task(db_container.reflection_service.get_reflection, dto)
    return Result.success("已提交分析任务")


@app.post('/aggregation')
def aggregation(dto: AggregationRequest):
    logger.info(f"执行用户聚合分析任务，用户ID: {dto.user}")
    db_container.agg_service.generate_aggregate(dto.user)
    logger.info(f"用户聚合数据更新成功。")
    return Result.success()


@app.post('/getAggregation')
def get_aggregation(dto: AggregationRequest):
    logger.info(f"获取用户聚合分析结果，用户ID: {dto.user}")
    aggregate = db_container.agg_service.get_aggregate(dto.user)
    logger.info(f"用户聚合分析结果检索成功。")
    return Result.success(data=AggregationResponse.from_orm(aggregate))


@app.post('/getSessions', response_model=Result[list[SessionRes]])
def get_sessions(dto: SessionRequest):
    logger.info(f"获取用户会话列表，用户ID: {dto.user}")
    sessions = db_container.session_service.get_sessions(dto.user)
    logger.info(f"成功检索到 {len(sessions)} 条会话记录。")
    return Result.success(data=sessions)


@app.post('/createSession')
def create_session(dto: SessionRequest):
    logger.info(f"为用户 [{dto.user}] 创建新会话。")
    session = db_container.session_service.create_session(dto.user, dto.message)
    logger.info(f"会话创建成功，SessionID: {session.id}")
    return Result.success(data=session.id)


@app.post('/renameSession')
def rename_session(dto: SessionRenameRequest):
    logger.info(f"执行会话重命名操作，SessionID: {dto.session_id}, 新标题: {dto.title}")
    session = db_container.session_service.rename_session(dto.session_id, dto.title)
    if session:
        logger.info(f"会话 [{dto.session_id}] 已成功重命名。")
        return Result.success("重命名成功")
    logger.warning(f"会话 [{dto.session_id}] 重命名失败。")
    return Result.fail("重命名失败")


@app.post('/deleteSession')
def delete_session(dto: SessionDeleteRequest):
    logger.info(f"执行会话删除操作，SessionID: {dto.session_id}")
    success = db_container.session_service.delete_session(dto.session_id)
    if success:
        logger.info(f"会话 [{dto.session_id}] 及其相关记录已成功删除。")
        return Result.success("删除成功")
    logger.error(f"会话 [{dto.session_id}] 删除失败。")
    return Result.fail("删除失败")


@app.post('/generateUserTags')
async def generate_tags(dto: UserRequest, background_tasks: BackgroundTasks):
    logger.info(f"提交用户标签生成任务，用户ID: {dto.user}")
    background_tasks.add_task(db_container.user_service.generate_tag, dto.user)
    return Result.success("请求已经成功发出")


@app.post('/getUser', response_model=Result[UserRes])
def get_user(dto: UserRequest):
    logger.info(f"检索用户信息，用户ID: {dto.user}")
    user = db_container.user_service.get_user(dto.user)
    if user:
        logger.info(f"用户信息检索成功。")
        return Result.success(data=UserRes.from_orm(user))
    logger.warning(f"用户信息不存在，用户ID: {dto.user}")
    return Result.fail("用户不存在")


@app.get('/getChats/{session_id}', response_model=Result[ChatListRes])
def get_chats(session_id: int):
    logger.info(f"检索会话历史记录，SessionID: {session_id}")
    chats = db_container.chat_service.get_chats(session_id)
    logger.info(f"成功检索到 {len(chats)} 条聊天记录。")
    result = ChatListRes(
        chats=chats,
        session_id=session_id
    )
    return Result.success(data=result)


@app.post('/chat')
def chat(dto: ChatRequest):
    logger.info(f"接收到对话请求：用户=[{dto.user}], SessionID=[{dto.session_id}]")
    ans = db_container.chat_service.generate_chat(dto.user, dto.session_id, dto.message)
    logger.info(f"Agent 响应生成完毕，准备持久化交互记录。")
    db_container.chat_service.save_chat(dto.session_id, 0, dto.message)
    db_container.chat_service.save_chat(dto.session_id, 1, ans)
    logger.info(f"对话交互记录持久化成功。")
    return Result.success(data=ans)

@app.post('/info_chat')
def chat(dto: ChatRequest):
    logger.info(f"接收到对话请求：用户=[{dto.user}], SessionID=[{dto.session_id}]")
    ans = db_container.info_chat_service.generate_chat(dto.user, dto.session_id, dto.message)
    logger.info(f"Agent 响应生成完毕，准备持久化交互记录。")
    db_container.info_chat_service.save_chat(dto.session_id, 0, dto.message)
    db_container.info_chat_service.save_chat(dto.session_id, 1, ans)
    logger.info(f"对话交互记录持久化成功。")
    return Result.success(data=ans)

