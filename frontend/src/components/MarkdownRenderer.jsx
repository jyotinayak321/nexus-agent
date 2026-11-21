import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Safely converts structured JSON / object payloads into readable Markdown.
 */
function formatJsonToMarkdown(data, depth = 1) {
  if (data === null || data === undefined) return "";

  if (typeof data !== "object") {
    return String(data);
  }

  if (Array.isArray(data)) {
    if (data.length === 0) return "*Empty list*";

    const isListOfObjects = data.every(
      (item) => typeof item === "object" && item !== null && !Array.isArray(item)
    );

    // If it's a list of objects with uniform keys, convert to a clean GFM table
    if (isListOfObjects && data.length > 0) {
      const keys = Array.from(new Set(data.flatMap((obj) => Object.keys(obj))));
      if (keys.length <= 6) {
        const header = `| ${keys.map((k) => k.replace(/_/g, " ").toUpperCase()).join(" | ")} |`;
        const separator = `| ${keys.map(() => "---").join(" | ")} |`;
        const rows = data.map(
          (obj) =>
            `| ${keys
              .map((k) => String(obj[k] ?? "-").replace(/\|/g, "\\|"))
              .join(" | ")} |`
        );
        return [header, separator, ...rows].join("\n");
      }
    }

    return data
      .map((item, idx) => {
        if (typeof item === "object" && item !== null) {
          const itemHeading =
            depth <= 2 ? `\n#### Item ${idx + 1}\n` : `\n- **Item ${idx + 1}**: `;
          return itemHeading + formatJsonToMarkdown(item, depth + 1);
        }
        return `- ${item}`;
      })
      .join("\n");
  }

  // It's a key-value object
  return Object.entries(data)
    .map(([key, val]) => {
      const title = key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
      if (val === null || val === undefined) return `- **${title}**: N/A`;
      if (typeof val === "object") {
        const headingPrefix = depth === 1 ? `### ${title}\n` : `\n**${title}**:\n`;
        return headingPrefix + formatJsonToMarkdown(val, depth + 1);
      }
      return `- **${title}**: ${val}`;
    })
    .join("\n\n");
}

/**
 * Preprocesses literal <br> strings safely without arbitrary HTML injection.
 * - Outside tables: turns '<br>• ' into proper indented list items and '<br>' into Markdown hard breaks.
 * - Inside tables: keeps '<br>' intact so table rows aren't split; custom component replaces it with <br />.
 */
function preprocessContent(content) {
  if (!content) return "";

  let text = "";
  if (typeof content === "object") {
    text = formatJsonToMarkdown(content);
  } else if (typeof content === "string") {
    const trimmed = content.trim();
    if (
      (trimmed.startsWith("{") && trimmed.endsWith("}")) ||
      (trimmed.startsWith("[") && trimmed.endsWith("]"))
    ) {
      try {
        const parsed = JSON.parse(trimmed);
        if (typeof parsed === "object" && parsed !== null) {
          text = formatJsonToMarkdown(parsed);
        } else {
          text = content;
        }
      } catch {
        text = content;
      }
    } else {
      text = content;
    }
  } else {
    text = String(content);
  }

  const lines = text.split("\n");
  const processed = lines.map((line) => {
    // If it's a table row, leave <br> for the td/th component to handle safely
    if (line.trim().startsWith("|")) {
      return line;
    }
    // Convert <br>• to indented list items
    let updated = line.replace(/<br\s*\/?>\s*•\s*/gi, "\n    - ");
    // Convert standalone <br> to Markdown hard line breaks (two trailing spaces + newline)
    updated = updated.replace(/<br\s*\/?>/gi, "  \n");
    return updated;
  });

  return processed.join("\n");
}

/**
 * Safely renders string children with literal <br> split into React <br /> elements.
 */
function renderWithSafeBreaks(child) {
  if (typeof child === "string") {
    const parts = child.split(/<br\s*\/?>/gi);
    if (parts.length > 1) {
      return parts.map((part, i) => (
        <React.Fragment key={i}>
          {i > 0 && <br />}
          {part}
        </React.Fragment>
      ));
    }
  }
  return child;
}

export default function MarkdownRenderer({ content, className = "" }) {
  if (!content) return null;

  const preprocessed = preprocessContent(content);

  const customComponents = {
    // Responsive table styling
    table: ({ node, ...props }) => (
      <div className="overflow-x-auto my-4 rounded-lg border border-gray-200 shadow-xs">
        <table className="min-w-full divide-y divide-gray-200 text-left text-xs" {...props} />
      </div>
    ),
    thead: ({ node, ...props }) => (
      <thead className="bg-slate-50 text-slate-700 font-semibold uppercase tracking-wider text-[11px]" {...props} />
    ),
    tbody: ({ node, ...props }) => (
      <tbody className="divide-y divide-gray-100 bg-white" {...props} />
    ),
    tr: ({ node, ...props }) => (
      <tr className="hover:bg-slate-50/75 transition-colors" {...props} />
    ),
    th: ({ node, children, ...props }) => (
      <th className="px-3.5 py-2.5 font-bold text-slate-800" {...props}>
        {React.Children.map(children, renderWithSafeBreaks)}
      </th>
    ),
    td: ({ node, children, ...props }) => (
      <td className="px-3.5 py-2.5 text-slate-700 align-top leading-relaxed" {...props}>
        {React.Children.map(children, renderWithSafeBreaks)}
      </td>
    ),

    // Headings hierarchy
    h1: ({ node, ...props }) => (
      <h1 className="text-xl font-bold text-slate-900 mt-6 mb-3 pb-2 border-b border-gray-200 tracking-tight" {...props} />
    ),
    h2: ({ node, ...props }) => (
      <h2 className="text-lg font-bold text-slate-900 mt-5 mb-2.5 tracking-tight flex items-center gap-2" {...props} />
    ),
    h3: ({ node, ...props }) => (
      <h3 className="text-base font-semibold text-slate-800 mt-4 mb-2 tracking-tight" {...props} />
    ),
    h4: ({ node, ...props }) => (
      <h4 className="text-sm font-semibold text-slate-800 mt-3 mb-1.5" {...props} />
    ),

    // Paragraphs and typography
    p: ({ node, children, ...props }) => (
      <p className="text-sm text-slate-700 leading-relaxed my-2.5" {...props}>
        {React.Children.map(children, renderWithSafeBreaks)}
      </p>
    ),
    ul: ({ node, ...props }) => (
      <ul className="list-disc pl-5 my-2.5 space-y-1.5 text-sm text-slate-700" {...props} />
    ),
    ol: ({ node, ...props }) => (
      <ol className="list-decimal pl-5 my-2.5 space-y-1.5 text-sm text-slate-700" {...props} />
    ),
    li: ({ node, children, ...props }) => (
      <li className="leading-relaxed text-slate-700" {...props}>
        {React.Children.map(children, renderWithSafeBreaks)}
      </li>
    ),
    blockquote: ({ node, ...props }) => (
      <blockquote className="border-l-4 border-orange-500 bg-orange-50/60 pl-4 py-2.5 my-3.5 rounded-r-lg text-xs sm:text-sm text-slate-800 italic space-y-1" {...props} />
    ),
    code: ({ node, inline, className, children, ...props }) => {
      if (inline) {
        return (
          <code className="bg-slate-100 text-orange-700 px-1.5 py-0.5 rounded text-xs font-mono font-medium border border-slate-200" {...props}>
            {children}
          </code>
        );
      }
      return (
        <code className="block bg-slate-900 text-emerald-400 p-3.5 rounded-lg overflow-x-auto text-xs font-mono leading-relaxed" {...props}>
          {children}
        </code>
      );
    },
    pre: ({ node, ...props }) => (
      <pre className="my-3 rounded-lg overflow-hidden" {...props} />
    ),
    hr: ({ node, ...props }) => (
      <hr className="my-6 border-gray-200" {...props} />
    ),
    a: ({ node, ...props }) => (
      <a className="text-orange-600 hover:text-orange-700 underline underline-offset-2 font-medium" target="_blank" rel="noopener noreferrer" {...props} />
    ),
    strong: ({ node, ...props }) => (
      <strong className="font-semibold text-slate-900" {...props} />
    ),
  };

  return (
    <div className={`markdown-content max-w-none text-slate-800 ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={customComponents}>
        {preprocessed}
      </ReactMarkdown>
    </div>
  );
}
