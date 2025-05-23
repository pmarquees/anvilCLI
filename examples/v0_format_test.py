#!/usr/bin/env python3
"""
Test script to verify that anvil can parse v0's file format correctly.
"""

import re
from typing import Dict

# Sample v0 response with the file="filename" format
V0_RESPONSE = '''
## Implementation

Let's start by creating our game components:

```tsx file="app/page.tsx"
import TicTacToe from '@/components/tic-tac-toe'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-gray-50">
      <h1 className="text-4xl font-bold mb-8 text-gray-800">Tic Tac Toe</h1>
      <TicTacToe />
    </main>
  )
}
```

Now, let's create the main game component:

```tsx file="components/tic-tac-toe.tsx"
'use client'

import { useState } from 'react'
import Square from './square'

export default function TicTacToe() {
  const [squares, setSquares] = useState<(string | null)[]>(Array(9).fill(null))
  const [xIsNext, setXIsNext] = useState<boolean>(true)

  const winner = calculateWinner(squares)
  const isDraw = !winner && squares.every(square => square !== null)

  const status = winner
    ? `Winner: ${winner}`
    : isDraw
    ? 'Draw!'
    : `Next player: ${xIsNext ? 'X' : 'O'}`

  function handleClick(i: number) {
    if (squares[i] || calculateWinner(squares)) {
      return
    }

    const nextSquares = squares.slice()
    nextSquares[i] = xIsNext ? 'X' : 'O'

    setSquares(nextSquares)
    setXIsNext(!xIsNext)
  }

  function resetGame() {
    setSquares(Array(9).fill(null))
    setXIsNext(true)
  }

  return (
    <div className="flex flex-col items-center">
      <div className="mb-4 text-xl font-medium text-gray-700">{status}</div>
      <div className="grid grid-cols-3 gap-2 mb-4">
        {Array.from({ length: 9 }, (_, i) => (
          <Square
            key={i}
            value={squares[i]}
            onSquareClick={() => handleClick(i)}
          />
        ))}
      </div>
      <button
        onClick={resetGame}
        className="px-4 py-2 mt-4 font-medium text-white bg-emerald-600 rounded-md hover:bg-emerald-700"
      >
        Reset Game
      </button>
    </div>
  )
}

function calculateWinner(squares: (string | null)[]) {
  const lines = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6]
  ]

  for (let i = 0; i < lines.length; i++) {
    const [a, b, c] = lines[i]
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a]
    }
  }
  return null
}
```

Let's also create the Square component:

```tsx file="components/square.tsx"
interface SquareProps {
  value: string | null
  onSquareClick: () => void
}

export default function Square({ value, onSquareClick }: SquareProps) {
  return (
    <button
      className="w-16 h-16 text-2xl font-bold border-2 border-gray-400 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
      onClick={onSquareClick}
    >
      {value}
    </button>
  )
}
```

And finally, let's add some styling:

```css file="app/globals.css"
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
```
'''

def parse_code_blocks(content: str) -> Dict[str, str]:
    """Parse code blocks from markdown content and extract filename and code."""
    files = {}
    
    # Pattern to match code blocks with various filename formats:
    # 1. ```tsx file="app/page.tsx" (v0 format)
    # 2. ```tsx:filename.tsx (colon format)  
    # 3. ```filename.tsx (direct filename)
    pattern = r'```(?:(\w+)\s+file="([^"]+)"|(\w+):([^\n]+\.(tsx?|jsx?|py|css|html|json|md|yml|yaml|toml|sh|txt))|([^\n]+\.(tsx?|jsx?|py|css|html|json|md|yml|yaml|toml|sh|txt)))\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        language_v0, filename_v0, language_colon, filename_colon, ext_colon, filename_direct, ext_direct, code = match
        
        # Handle v0 format: ```tsx file="app/page.tsx"
        if language_v0 and filename_v0:
            files[filename_v0] = code.strip()
        # Handle colon format: ```tsx:filename.tsx
        elif language_colon and filename_colon:
            files[filename_colon] = code.strip()
        # Handle direct filename: ```filename.tsx
        elif filename_direct:
            files[filename_direct] = code.strip()
    
    return files

def test_v0_parsing():
    """Test that we can parse v0's file format correctly."""
    print("🧪 Testing v0 format parsing...")
    print("=" * 50)
    
    files = parse_code_blocks(V0_RESPONSE)
    
    print(f"📁 Found {len(files)} files:")
    for filename, content in files.items():
        print(f"  ✅ {filename} ({len(content)} characters)")
        # Show first few lines of content
        lines = content.split('\n')[:3]
        for line in lines:
            if line.strip():
                print(f"      {line[:60]}{'...' if len(line) > 60 else ''}")
        print()
    
    # Check expected files
    expected_files = [
        "app/page.tsx",
        "components/tic-tac-toe.tsx", 
        "components/square.tsx",
        "app/globals.css"
    ]
    
    print("✅ Expected files:")
    for expected in expected_files:
        if expected in files:
            print(f"  ✅ {expected} - Found")
        else:
            print(f"  ❌ {expected} - Missing")
    
    return files

if __name__ == "__main__":
    test_v0_parsing() 