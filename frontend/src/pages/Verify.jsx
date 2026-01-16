import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

export default function Verify() {
  const [result, setResult] = useState(null);
  const query = new URLSearchParams(useLocation().search);
  const jobId = query.get("job_id");

  useEffect(()=>{
    const timer = setInterval(async ()=>{
      const res = await fetch(`http://localhost:8000/result/${jobId}`);
      const json = await res.json();
      if(json.status !== "processing"){
        setResult(json);
        clearInterval(timer);
      }
    }, 3000);
  }, []);

  if(!result) return <p>Processing...</p>;
  return <pre>{JSON.stringify(result,null,2)}</pre>;
}
