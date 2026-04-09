let expression = '';
let justCalculated = false;

// Safe arithmetic expression parser (no eval)
// Supports: +, -, *, /, % (as modulo) on numbers with decimals and unary minus
function parseExpression(tokens, pos) {
  let [left, p] = parseTerm(tokens, pos);
  while (p < tokens.length && (tokens[p] === '+' || tokens[p] === '-')) {
    const op = tokens[p++];
    const [right, next] = parseTerm(tokens, p);
    left = op === '+' ? left + right : left - right;
    p = next;
  }
  return [left, p];
}

function parseTerm(tokens, pos) {
  let [left, p] = parseUnary(tokens, pos);
  while (p < tokens.length && (tokens[p] === '*' || tokens[p] === '/' || tokens[p] === '%')) {
    const op = tokens[p++];
    const [right, next] = parseUnary(tokens, p);
    if (op === '*') left = left * right;
    else if (op === '/') {
      if (right === 0) throw new Error('Division by zero');
      left = left / right;
    }
    else left = left % right;
    p = next;
  }
  return [left, p];
}

function parseUnary(tokens, pos) {
  if (tokens[pos] === '-') {
    const [val, next] = parseUnary(tokens, pos + 1);
    return [-val, next];
  }
  if (tokens[pos] === '+') {
    return parseUnary(tokens, pos + 1);
  }
  return parseNumber(tokens, pos);
}

function parseNumber(tokens, pos) {
  if (pos >= tokens.length) throw new Error('Unexpected end');
  const num = parseFloat(tokens[pos]);
  if (isNaN(num)) throw new Error('Expected number, got: ' + tokens[pos]);
  return [num, pos + 1];
}

function tokenize(expr) {
  const tokens = [];
  let i = 0;
  while (i < expr.length) {
    const ch = expr[i];
    if (ch === ' ') { i++; continue; }
    if ('+-*/%'.includes(ch)) {
      tokens.push(ch);
      i++;
    } else if ((ch >= '0' && ch <= '9') || ch === '.') {
      let num = '';
      while (i < expr.length && ((expr[i] >= '0' && expr[i] <= '9') || expr[i] === '.')) {
        num += expr[i++];
      }
      tokens.push(num);
    } else {
      throw new Error('Unknown character: ' + ch);
    }
  }
  return tokens;
}

function safeEval(expr) {
  const tokens = tokenize(expr);
  if (tokens.length === 0) return NaN;
  const [result, pos] = parseExpression(tokens, 0);
  if (pos !== tokens.length) throw new Error('Unexpected token: ' + tokens[pos]);
  return result;
}

function updateDisplay() {
  const expressionEl = document.getElementById('expression');
  const resultEl = document.getElementById('result');

  expressionEl.textContent = expression
    .replace(/\*/g, '×')
    .replace(/\//g, '÷');

  if (expression === '') {
    resultEl.textContent = '0';
  } else {
    try {
      const value = safeEval(expression);
      if (!isNaN(value) && isFinite(value)) {
        resultEl.textContent = formatNumber(value);
      }
    } catch {
      // expression is incomplete, keep showing current result
    }
  }
}

function formatNumber(num) {
  const str = String(num);
  if (str.includes('e')) {
    return num.toExponential(6);
  }
  if (str.includes('.')) {
    const parts = str.split('.');
    if (parts[1].length > 10) {
      return parseFloat(num.toFixed(10)).toString();
    }
  }
  return str;
}

function appendToExpression(value) {
  const operators = ['+', '-', '*', '/', '%'];

  if (justCalculated) {
    // After equals, operator continues from result; digit starts fresh
    if (operators.includes(value)) {
      const currentResult = document.getElementById('result').textContent;
      expression = currentResult + value;
    } else {
      expression = value;
    }
    justCalculated = false;
  } else {
    const last = expression.slice(-1);

    // Prevent consecutive operators (except minus for negation after operator)
    if (operators.includes(value) && operators.includes(last)) {
      if (value === '-') {
        expression += value;
      } else {
        expression = expression.slice(0, -1) + value;
      }
    } else if (value === '.' && expression.split(/[+\-*/%]/).pop().includes('.')) {
      // Prevent multiple dots in the same number
      return;
    } else {
      expression += value;
    }
  }

  updateDisplay();
}

function calculate() {
  if (expression === '') return;

  try {
    const value = safeEval(expression);
    if (isNaN(value) || !isFinite(value)) {
      document.getElementById('result').textContent = 'Ошибка';
      expression = '';
      justCalculated = false;
      return;
    }
    const resultStr = formatNumber(value);
    document.getElementById('expression').textContent =
      expression.replace(/\*/g, '×').replace(/\//g, '÷') + ' =';
    document.getElementById('result').textContent = resultStr;
    expression = resultStr;
    justCalculated = true;
  } catch {
    document.getElementById('result').textContent = 'Ошибка';
    expression = '';
    justCalculated = false;
  }
}

function clearAll() {
  expression = '';
  justCalculated = false;
  document.getElementById('expression').textContent = '';
  document.getElementById('result').textContent = '0';
}

function deleteLast() {
  if (justCalculated) {
    clearAll();
    return;
  }
  expression = expression.slice(0, -1);
  updateDisplay();
}

document.addEventListener('keydown', (e) => {
  if (e.key >= '0' && e.key <= '9') appendToExpression(e.key);
  else if (e.key === '+') appendToExpression('+');
  else if (e.key === '-') appendToExpression('-');
  else if (e.key === '*') appendToExpression('*');
  else if (e.key === '/') { e.preventDefault(); appendToExpression('/'); }
  else if (e.key === '%') appendToExpression('%');
  else if (e.key === '.') appendToExpression('.');
  else if (e.key === 'Enter' || e.key === '=') calculate();
  else if (e.key === 'Backspace') deleteLast();
  else if (e.key === 'Escape') clearAll();
});

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const action = btn.dataset.action;
      const value = btn.dataset.value;
      if (action === 'clear') clearAll();
      else if (action === 'delete') deleteLast();
      else if (action === 'calculate') calculate();
      else if (value !== undefined) appendToExpression(value);
    });
  });
});
