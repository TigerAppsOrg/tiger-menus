// run with node tests/hall-active.cjs
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const vm = require('node:vm');

function element() {
  return {
    style: { setProperty() {} }, classList: { toggle() {} },
    attributes: {}, children: [],
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    append(child) { this.children.push(child); },
    addEventListener() {}
  };
}

const headings = ['Choi', 'CJL', 'Whitman'].map((name, index) => ({
  ...element(), id: `hall-${index + 1}`, textContent: name, dataset: { hallName: name }, top: 0,
  getBoundingClientRect() { return { top: this.top }; }
}));
headings[0].textContent = 'Choi (Huo/Yeh)';
const body = element();
const context = vm.createContext({
  document: {
    querySelectorAll: () => headings, createElement: element,
    body, documentElement: { scrollHeight: 3000 }
  },
  matchMedia: () => ({ matches: true }), innerHeight: 900, scrollY: 400,
  addEventListener() {}
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
console.log('Short hall active-state regression passed');
