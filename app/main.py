from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.prompts.templates import MODES
from app.schemas import AskRequest, BenchmarkRequest
from app.services import llm, vector_store
from app.services.loaders import read_file

app = FastAPI(title="Lexicon - Document Q&A")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_methods=["*"], allow_headers=["*"])
api = APIRouter(prefix="/api")


@app.exception_handler(llm.LLMError)
async def llm_error(_, exc: llm.LLMError):
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@api.get("/health")
def health():
    return {"status": "ok"}


@api.get("/docs-list")
def docs():
    return vector_store.list_documents()


@api.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    out = []
    for f in files:
        if not f.filename.lower().endswith(settings.allowed_ext):
            raise HTTPException(400, f"{f.filename}: only PDF, TXT and MD files are supported")
        n = vector_store.add_document(f.filename, read_file(f.filename, await f.read()))
        out.append({"name": f.filename, "chunks": n})
    return out


@api.post("/ask")
def ask(body: AskRequest):
    if body.mode not in MODES:
        raise HTTPException(400, "mode must be zero_shot, few_shot or role_based")
    chunks = vector_store.semantic_search(body.question, settings.top_k)
    return {"answer": llm.answer(body.mode, body.question, chunks), "chunks": chunks}


@api.get("/search")
def search(q: str):
    return {"semantic": vector_store.semantic_search(q, settings.top_k),
            "keyword": vector_store.keyword_search(q, settings.top_k)}


@api.post("/benchmark")
def benchmark(body: BenchmarkRequest):
    retrieved = {q: vector_store.semantic_search(q, settings.top_k) for q in body.questions}

    def run(pair):
        q, mode = pair
        ans = llm.answer(mode, q, retrieved[q])
        return q, mode, {"answer": ans, "scores": llm.judge(q, retrieved[q], ans)}

    pairs = [(q, m) for q in body.questions for m in MODES]
    with ThreadPoolExecutor(max_workers=6) as pool:
        done = list(pool.map(run, pairs))
    table = {q: {} for q in body.questions}
    for q, mode, res in done:
        table[q][mode] = res
    results = [{"question": q, "runs": table[q]} for q in body.questions]
    n = max(len(body.questions), 1)
    avg = {m: round(sum(table[q][m]["scores"]["avg"] for q in body.questions) / n, 2) for m in MODES}
    return {"results": results, "averages": avg, "best": max(avg, key=avg.get)}


app.include_router(api)
if settings.public_dir.exists():  # local run; on Vercel the CDN serves /public
    app.mount("/", StaticFiles(directory=settings.public_dir, html=True), name="public")
