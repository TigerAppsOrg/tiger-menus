const hallHeadings = [...document.querySelectorAll('.dining-hall h2')];
const hallNav = document.createElement('nav');
hallNav.className = 'hall-rail';
hallNav.setAttribute('aria-label', 'Dining halls');
hallNav.inert = true;
hallNav.style.setProperty('--hall-count', hallHeadings.length);
const hallLinks = hallHeadings.map(heading => {
  const link = document.createElement('a');
  link.href = `#${heading.id}`;
  link.textContent = heading.dataset.hallName;
  link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    heading.focus({ preventScroll: true });
    heading.scrollIntoView({
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',
      block: 'start'
    });
    scheduleHallRail();
  });
  hallNav.append(link);
  return link;
});
const marker = document.createElement('span');
marker.className = 'hall-marker';
marker.setAttribute('aria-hidden', 'true');
hallNav.append(marker);
document.body.append(hallNav);

let hallFrame = 0;
function updateHallRail() {
  hallFrame = 0;
  const visible = matchMedia('(max-width: 767px)').matches && hallHeadings[0].getBoundingClientRect().top < 24;
  hallNav.classList.toggle('is-visible', visible);
  hallNav.inert = !visible;
  if (!visible) return;
  let active = 0;
  hallHeadings.forEach((heading, index) => {
    if (heading.getBoundingClientRect().top <= 24) active = index;
  });
  if (scrollY + innerHeight >= document.documentElement.scrollHeight - 4) {
    const focused = hallHeadings.indexOf(document.activeElement);
    const top = focused >= 0 ? hallHeadings[focused].getBoundingClientRect().top : -1;
    active = top >= 0 && top < innerHeight ? focused : hallHeadings.length - 1;
  }
  hallNav.style.setProperty('--hall-index', active);
  hallLinks.forEach((link, index) => {
    if (index === active) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}
function scheduleHallRail() {
  if (!hallFrame) hallFrame = requestAnimationFrame(updateHallRail);
}
addEventListener('scroll', scheduleHallRail, { passive: true });
addEventListener('resize', scheduleHallRail);
updateHallRail();
