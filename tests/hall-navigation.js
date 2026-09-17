// run with agent-browser eval --stdin < tests/hall-navigation.js on a mobile viewport
(async () => {
  const headings = [...document.querySelectorAll('.dining-hall h2')];
  const nav = document.querySelector('.hall-rail');
  const links = [...nav.querySelectorAll('a')];
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  const settle = () => new Promise(resolve => setTimeout(resolve, 1000));
  assert(links.length === headings.length, 'Every hall has a link');
  window.scrollTo({ top: 0, behavior: 'instant' });
  await settle();
  assert(nav.inert && !nav.classList.contains('is-visible'), 'Rail is hidden at the top');
  for (const index of [headings.length - 1, 1, 0]) {
    links[index].click();
    await settle();
    assert(document.activeElement === headings[index], 'Focus follows the selected hall');
    assert(nav.classList.contains('is-visible') && !nav.inert, 'Rail appears after scrolling');
    assert(links[index].getAttribute('aria-current') === 'location', 'Current hall is highlighted');
    assert(headings[index].getBoundingClientRect().top >= 0, 'Heading is visible');
  }
  assert(document.documentElement.scrollWidth <= innerWidth, 'No horizontal overflow');
  return 'Hall navigation passed';
})();
