#!/usr/bin/env python3
"""
Demo script showing how the anvil sketch command works.
This simulates the v0 API response for educational purposes.
"""

import os
import time
from pathlib import Path

# Simulate a v0 API response with streaming
SAMPLE_RESPONSE = """# React Todo App

Here's a modern React todo app with dark mode support:

```tsx:components/TodoApp.tsx
import React, { useState, useEffect } from 'react';
import './TodoApp.css';

interface Todo {
  id: number;
  text: string;
  completed: boolean;
}

export default function TodoApp() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState('');
  const [darkMode, setDarkMode] = useState(false);

  const addTodo = () => {
    if (input.trim()) {
      setTodos([...todos, {
        id: Date.now(),
        text: input.trim(),
        completed: false
      }]);
      setInput('');
    }
  };

  const toggleTodo = (id: number) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const deleteTodo = (id: number) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  return (
    <div className={`app ${darkMode ? 'dark' : ''}`}>
      <header>
        <h1>Todo App</h1>
        <button onClick={() => setDarkMode(!darkMode)}>
          {darkMode ? '☀️' : '🌙'}
        </button>
      </header>
      
      <div className="input-section">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addTodo()}
          placeholder="Add a new todo..."
        />
        <button onClick={addTodo}>Add</button>
      </div>

      <ul className="todo-list">
        {todos.map(todo => (
          <li key={todo.id} className={todo.completed ? 'completed' : ''}>
            <span onClick={() => toggleTodo(todo.id)}>{todo.text}</span>
            <button onClick={() => deleteTodo(todo.id)}>×</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

```css:components/TodoApp.css
.app {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', roboto, sans-serif;
  background: #f5f5f5;
  min-height: 100vh;
  transition: all 0.3s ease;
}

.app.dark {
  background: #1a1a1a;
  color: #fff;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.input-section {
  display: flex;
  gap: 10px;
  margin-bottom: 2rem;
}

.input-section input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
}

.app.dark .input-section input {
  background: #333;
  border-color: #555;
  color: #fff;
}

.input-section button {
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

.todo-list {
  list-style: none;
  padding: 0;
}

.todo-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border-radius: 8px;
  cursor: pointer;
}

.app.dark .todo-list li {
  background: #333;
}

.todo-list li.completed {
  opacity: 0.6;
  text-decoration: line-through;
}

.todo-list li button {
  background: #ff4757;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
}
```

```json:package.json
{
  "name": "todo-app",
  "version": "1.0.0",
  "description": "A modern React todo app with dark mode",
  "main": "index.js",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next": "^14.0.0",
    "typescript": "^5.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0"
  }
}
```

This todo app includes:
- ✅ Add, toggle, and delete todos
- 🌙 Dark mode toggle
- 📱 Responsive design
- ⚡ TypeScript support
- 🎨 Modern CSS styling

To get started:
1. Run `npm install`
2. Run `npm run dev`
3. Open http://localhost:3000
"""


def simulate_streaming_output():
    """Simulate the streaming output that anvil sketch would produce."""
    print("🚀 Calling v0 API...")
    print()
    print("🤖 v0 Response:")
    print("┌" + "─" * 50 + "┐")
    
    # Simulate streaming by printing chunks with delays
    for chunk in SAMPLE_RESPONSE.split():
        print(chunk, end=" ", flush=True)
        time.sleep(0.05)  # Small delay to simulate streaming
    
    print()
    print("└" + "─" * 50 + "┘")
    print("=" * 50)
    
    print("\n📁 Creating 3 file(s):")
    print("  ✅ Created: components/TodoApp.tsx")
    print("  ✅ Created: components/TodoApp.css") 
    print("  ✅ Created: package.json")


if __name__ == "__main__":
    print("📝 Prompt: Create a Next.js todo app with dark mode")
    print("📂 Working directory: /current/directory")
    print()
    
    # Check if we're just demonstrating
    if not os.getenv("V0_API_KEY"):
        print("📋 Demo Mode - This shows what the output would look like")
        print("   To use for real, set V0_API_KEY environment variable")
        print()
    
    simulate_streaming_output() 