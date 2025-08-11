import './App.css'

function App() {
  return (
    <div className="App">
      <h1>Meeting Summary App</h1>
      <p>基本的な動作確認中</p>
      <div>
        <h2>認証テスト</h2>
        <button onClick={() => alert('Google認証テスト')}>
          Google認証テスト
        </button>
        <button onClick={() => alert('LINE認証テスト')}>
          LINE認証テスト
        </button>
        <button onClick={() => alert('メール認証テスト')}>
          メール認証テスト
        </button>
      </div>
    </div>
  )
}

export default App