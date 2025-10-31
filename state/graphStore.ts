// state/graphStore.ts
"use client";
type Sub = () => void;
const w = typeof window !== "undefined" ? (window as any) : {};
if (!w.__MP_GRAPH__) {
  let version = 0; const subs = new Set<Sub>();
  const ref = { nodes: new Map<string, any>(), links: new Map<string, any>() };
  w.__MP_GRAPH__ = {
    ref,
    subscribe: (fn:Sub)=>{ subs.add(fn); return ()=>subs.delete(fn); },
    getVersion: ()=>version,
    applyNode: (n:any)=>{ if(n?.id) ref.nodes.set(n.id,n); },
    applyLink: (l:any)=>{ if(l?.id) ref.links.set(l.id,l); },
    flush: ()=>{ version++; subs.forEach(f=>f()); }
  };
}
export const graph = w.__MP_GRAPH__;
import { useSyncExternalStore, useMemo } from "react";
export function useGraph(){
  useSyncExternalStore(graph.subscribe, graph.getVersion, graph.getVersion);
  return useMemo(()=>({ nodes: graph.ref.nodes, links: graph.ref.links, version: graph.getVersion() }), [graph.getVersion()]);
}