import React, { useState } from "react";
import "./App.css"; // 스타일 파일을 가져옵니다.

export const MyPlugin = () => {
  const [inputText, setInputText] = useState(""); // 입력값 상태
  const [displayText, setDisplayText] = useState(""); // 화면 표시용 상태

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/process-user-text/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText }),
      });
      
      const data = await response.json();
      console.log('서버 응답:', data);
      setDisplayText(inputText); // 화면에 입력한 내용을 표시
      setInputText(""); // 입력 필드 초기화
    } catch (error) {
      console.error('에러:', error);
    }
  };

  return (
    <div id="webcrumbs">
      <div className="w-[1000px] bg-neutral-900 rounded-lg shadow-lg min-h-[600px] text-neutral-50 flex-row flex">
        {/* 사이드바 */}
        <aside className="w-[250px] bg-neutral-800 p-4 flex-col flex gap-4">
          <button className="flex items-center gap-2 py-2 px-4 rounded-md bg-primary-500 text-primary-50 text-sm hover:bg-primary-600">
            <span className="material-symbols-outlined">menu</span> 메뉴
          </button>
          <nav className="flex-col flex gap-2">
            <button className="text-neutral-300 rounded-md px-3 py-2 bg-neutral-700 hover:bg-neutral-600 text-sm flex items-center gap-2">
              <span className="material-symbols-outlined">folder</span> 항목 1
            </button>
            <button className="text-neutral-300 rounded-md px-3 py-2 bg-neutral-700 hover:bg-neutral-600 text-sm flex items-center gap-2">
              <span className="material-symbols-outlined">folder</span> 항목 2
            </button>
            <button className="text-neutral-300 rounded-md px-3 py-2 bg-neutral-700 hover:bg-neutral-600 text-sm flex items-center gap-2">
              <span className="material-symbols-outlined">folder</span> 항목 3
            </button>
          </nav>
        </aside>

        {/* 메인 컨텐츠 */}
        <div className="flex-1 flex-col flex">
          <header className="h-[60px] bg-neutral-800 flex items-center px-4">
            <button className="text-neutral-300 rounded-md px-3 py-2 bg-neutral-700 hover:bg-neutral-600 text-sm flex items-center gap-2">
              <span className="material-symbols-outlined">add</span> 문제 추가하기
            </button>
          </header>
          <main className="flex overflow-hidden flex-1">
            {/* 문제 섹션 */}
            <section className="w-1/2 p-4 overflow-auto border-r border-neutral-700">
              <h1 className="text-lg font-title mb-4">수능 영어의 아고라😎</h1>
              <p className="text-sm leading-relaxed">
                {displayText ? `${displayText}` : "🤖 튜터와 함께 공동 편집창에서 문제에 대한 이야기를 나눠보세요!"}
              </p>
            </section>
            {/* 해설 섹션 */}
            <section className="w-1/2 p-4 overflow-auto">
              <h1 className="text-lg font-title mb-4">AI 기반의 풍부한 해설💡</h1>
            </section>
          </main>
          <footer className="p-4 bg-neutral-800 flex justify-between items-center">
            <button className="flex items-center gap-2 py-2 px-4 rounded-md bg-primary-500 text-primary-50 text-sm hover:bg-primary-600">
              <span className="material-symbols-outlined">add_task</span>
              새로운 문제 생성
            </button>
            <form 
              onSubmit={handleSubmit} 
              className="w-full max-w-[700px] flex items-center gap-2 bg-neutral-700 rounded-md p-2"
            >
              <span className="material-symbols-outlined text-neutral-300">
                upload
              </span>
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Type your input..."
                className="flex-1 bg-transparent outline-none text-neutral-50"
              />
              <button 
                type="submit"
                className="py-2 px-4 rounded-md bg-primary-500 text-sm text-primary-50 hover:bg-primary-600"
              >
                <span className="material-symbols-outlined">send</span>
              </button>
            </form>
          </footer>
        </div>
      </div>
    </div>
  );
};
