import { Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Evaluate from "./pages/Evaluate";
import Verify from "./pages/Verify";
export default function Router() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/features" element={<Landing />} />
      <Route path="/evaluate" element={<Evaluate />} />
      <Route path="/verify" element={<Verify />} />
      <Route path="/contact" element={<Landing />} />
    </Routes>
  );
}