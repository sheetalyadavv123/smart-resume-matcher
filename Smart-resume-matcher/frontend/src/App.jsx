import { useEffect } from "react";

function App() {
  useEffect(() => {
    fetch("http://localhost:8000/test")
      .then(res => res.json())
      .then(data => console.log(data));
  }, []);

  return <h1>Frontend running</h1>;
}

export default App;
