/// <reference types="vite/client" />

// Declare module for raw text file imports
declare module '*.txt?raw' {
  const content: string;
  export default content;
}

declare module '*.html?raw' {
  const content: string;
  export default content;
}