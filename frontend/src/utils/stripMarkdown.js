export function stripMarkdown(text) {
  if (!text || typeof text !== 'string') return text
  return text
    .replace(/#{1,6}\s+/g, '')        // ## headings
    .replace(/\*\*(.+?)\*\*/g, '$1')  // **bold**
    .replace(/\*(.+?)\*/g, '$1')      // *italic*
    .replace(/`(.+?)`/g, '$1')        // `code`
    .replace(/^\s*[-*+]\s+/gm, '')    // bullet points
    .replace(/^\s*\d+\.\s+/gm, '')    // numbered lists
    .replace(/\[(.+?)\]\(.+?\)/g, '$1') // [links](url)
    .replace(/\n{3,}/g, '\n\n')       // extra newlines
    .trim()
}
