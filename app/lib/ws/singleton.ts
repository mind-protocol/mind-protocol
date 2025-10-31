'use client';
let ws: WebSocket|null=null, connecting=false;
export function ensureWS(url:string){
  if (ws && (ws.readyState===1 || ws.readyState===0)) return ws;
  if (connecting) return ws!Connecting=true;
  ws = new WebSocket(url);
  ws.addEventListener("open", ()=>{ connecting=false; });
  ws.addEventListener("close", ()=>{ connecting=false; });
  window.addEventListener("beforeunload", ()=>{ try{ws?.close(1000,"unload");}catch{} ws=null; });
  return ws!;
}
