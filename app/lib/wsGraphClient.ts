// lib/wsGraphClient.ts
"use client";
import { graph } from "@/state/graphStore";
const linkId = (l:{from:string;type:string;to:string}) => `l:${l.from}|${l.type}|${l.to}`;
let rafQueued=false; let pending={nodes:[] as any[], links:[] as any[]};

function scheduleFlush(){
  if (rafQueued) return; rafQueued = true;
  requestAnimationFrame(() => {
    for (const n of pending.nodes) graph.applyNode(n);
    for (const l of pending.links) graph.applyLink(l);
    pending = {nodes:[],links:[]}; graph.flush(); rafQueued=false;
  });
}

export function handleSnapshotChunk(chunk:any){
  if (chunk?.nodes) pending.nodes.push(...chunk.nodes);
  if (chunk?.links) pending.links.push(...chunk.links.map((l:any)=>({...l,id:l.id ?? linkId(l)})));
  scheduleFlush(); // and always on EOF:true
}