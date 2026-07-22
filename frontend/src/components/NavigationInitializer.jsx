import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { setNavigate } from "../navigation";

export default function NavigationInitializer() {
  const navigate = useNavigate();

  useEffect(() => {
    setNavigate(navigate);
  }, [navigate]);

  return null;
}