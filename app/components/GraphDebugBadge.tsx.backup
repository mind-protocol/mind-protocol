"use client";
import { useGraph } from "@/state/graphStore";
export default function GraphDebugBadge(){
  const { nodes, links, version } = useGraph();
  return <div style={{position:"fixed",right:8,bottom:8,zIndex:9999,
    padding:"6px 10px",background:"rgba(0,0,0,.7)",color:"#fff",fontSize:12}}>
    v{version} • nodes {nodes.size} • links {links.size}
  </div>;
}
