"""Question-answering chain with metadata-aware retrieval."""
import logging
from typing import Dict, List, Optional

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.vectorstore_manager import get_vectorstore_manager

logger = logging.getLogger(__name__)


class QAChain:
    """RAG QA chain builder and invoker."""

    def __init__(self):
        self.settings = get_settings()
        self.vectorstore_manager = get_vectorstore_manager()
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.0,
            openai_api_key=self.settings.openai_api_key,
            request_timeout=self.settings.openai_timeout,
        )
        self.prompt = PromptTemplate(
            template=(
                "You are a factual assistant. Use only the supplied context to answer.\n"
                "If the answer is not in context, say you do not know.\n"
                "Cite concise, relevant facts only.\n\n"
                "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
            ),
            input_variables=["context", "question"],
        )

    def answer_question(self, question: str, top_k: int, metadata_filter: Optional[Dict] = None) -> Dict[str, List[Document] | str]:
        if not self.vectorstore_manager.is_initialized():
            raise ValueError("No documents uploaded. Please upload documents first.")

        retriever = self.vectorstore_manager.vectorstore.as_retriever(
            search_kwargs={"k": top_k, **({"filter": metadata_filter} if metadata_filter else {})}
        )

        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt},
        )

        result = chain.invoke({"query": question})
        return {
            "answer": result["result"],
            "source_documents": result["source_documents"],
        }


_qa_chain: QAChain | None = None


def get_qa_chain() -> QAChain:
    """Return singleton QA chain."""
    global _qa_chain
    if _qa_chain is None:
        _qa_chain = QAChain()
    return _qa_chain
