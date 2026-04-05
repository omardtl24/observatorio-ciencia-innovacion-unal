import React from "react";

export function datetoString(date){
    return new Date(date).toLocaleDateString("es-ES", {
                year: "numeric",
                month: "long",
            }).replace(/^\w/, (c) => c.toUpperCase())
}


export function stripColorMarkers(text) {
  if (!text) return "";
  return text.replace(/\\\((.*?)\\\)/g, "$1");
}


export function parseColor(text, colorClass) {
  if (!text) return null;

  return text.split(/(\\\(.*?\\\))/g).map((part, i) => {
    const match = part.match(/\\\((.*?)\\\)/);

    if (match) {
      return (
        <span key={i} className={colorClass}>
          {match[1]}
        </span>
      );
    }

    return part;
  });
}


export function parseRichText(text, colorClass) {
  if (!text) return null;

  const applyColor = (line) => parseColor(line, colorClass);

  const normalizedText = text.replace(/\\n/g, "\n");
  const lines = normalizedText.split("\n");

  const blocks = [];
  let listBuffer = [];
  let listType = null;

  const flushList = () => {
    if (!listBuffer.length) return;

    blocks.push(
      listType === "ol" ? (
        <ol key={blocks.length} className="list-decimal ml-6 mb-4">
          {listBuffer.map((item, i) => (
            <li key={i}>{applyColor(item)}</li>
          ))}
        </ol>
      ) : (
        <ul key={blocks.length} className="list-disc ml-6 mb-4">
          {listBuffer.map((item, i) => (
            <li key={i}>{applyColor(item)}</li>
          ))}
        </ul>
      )
    );

    listBuffer = [];
    listType = null;
  };

  lines.forEach((line) => {
    const ordered = line.match(/^\s*\d+\.\s+(.*)/);
    const unordered = line.match(/^\s*\*\s+(.*)/);

    if (ordered) {
      if (listType !== "ol") flushList();
      listType = "ol";
      listBuffer.push(ordered[1]);
      return;
    }

    if (unordered) {
      if (listType !== "ul") flushList();
      listType = "ul";
      listBuffer.push(unordered[1]);
      return;
    }

    flushList();

    if (line.trim()) {
      blocks.push(
        <p key={blocks.length} className="mb-4 leading-relaxed">
          {applyColor(line)}
        </p>
      );
    }
  });

  flushList();
  return blocks;
}
