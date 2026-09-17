// run with node tests/hall-active.cjs
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const vm = require('node:vm');

function element() {
  return {
    style: { setProperty() {} }, classList: { toggle() {} },
    attributes: {}, children: [], listeners: {},
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    append(child) { this.children.push(child); },
    addEventListener(name, callback) { this.listeners[name] = callback; }
  };
}

const headings = ['Choi', 'CJL', 'Whitman'].map((name, index) => ({
  ...element(), id: `hall-${index + 1}`, textContent: name, dataset: { hallName: name }, top: 0,
  getBoundingClientRect() { return { top: this.top }; },
  focus() { context.document.activeElement = this; },
  scrollIntoView() {}
}));
headings[0].textContent = 'Choi (Huo/Yeh)';
const body = element();
const frames = [];
const context = vm.createContext({
  document: {
    querySelectorAll: () => headings, createElement: element,
    body, documentElement: { scrollHeight: 3000 }
  },
  matchMedia: () => ({ matches: true }), innerHeight: 900, scrollY: 400,
  addEventListener() {},
  requestAnimationFrame(callback) { frames.push(callback); return frames.length; }
});
vm.runInContext(readFileSync('app/static/menu.js', 'utf8'), context);

assert.equal(body.children[0].children[0].textContent, 'Choi');

for (const [tops, expected] of [
  [[16, 120, 220], 0], // short fallback halls below the selected heading
  [[-88, 16, 116], 1],
  [[-100, 25, 600], 0], // the next hall has not reached the reading line
  [[-100, 24, 600], 1]
]) {
  headings.forEach((heading, index) => { heading.top = tops[index]; });
  vm.runInContext('updateHallRail()', context);
  const active = body.children[0].children.findIndex(link => link.attributes['aria-current'] === 'location');
  assert.equal(active, expected, `Active hall at heading positions ${tops}`);
}
context.scrollY = 2100;
headings.forEach((heading, index) => { heading.top = [-200, 180, 280][index]; });
const links = body.children[0].children;
const activeHall = () => links.findIndex(link => link.attributes['aria-current'] === 'location');
context.document.activeElement = headings[1];
vm.runInContext('updateHallRail()', context);
assert.equal(activeHall(), 1, 'Clamped jump keeps a visible non-final hall active');
context.document.activeElement = headings[0];
vm.runInContext('updateHallRail()', context);
assert.equal(activeHall(), 2, 'An offscreen focused heading does not override the last hall');
context.document.activeElement = body;
vm.runInContext('updateHallRail()', context);
assert.equal(activeHall(), 2, 'Ordinary scrolling to the bottom selects the last hall');
links[1].listeners.click({ preventDefault() {} });
assert.equal(frames.length, 1, 'Clicking at the bottom schedules an update without a scroll event');
frames.shift()();
assert.equal(activeHall(), 1, 'A click at the existing bottom updates the active hall');
console.log('Hall active-state regressions passed');
