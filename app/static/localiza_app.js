const modes = [...document.querySelectorAll('.mode')];
const currentCopy = document.querySelector('.current-copy');
const futureCopy = document.querySelector('.future-copy');
const currentView = document.querySelector('.current-view');
const futureView = document.querySelector('.future-view');
const otherViews = [...document.querySelectorAll('.phone-view')].filter(v => !v.classList.contains('current-view') && !v.classList.contains('future-view'));
const navs = [...document.querySelectorAll('.nav')];
const serviceBacks = [...document.querySelectorAll('.back')];

function showMode(mode){
  modes.forEach(btn => btn.classList.toggle('active', btn.dataset.mode === mode));
  currentCopy.classList.toggle('active', mode === 'current');
  futureCopy.classList.toggle('active', mode === 'future');
  currentView.classList.toggle('active', mode === 'current');
  futureView.classList.toggle('active', mode === 'future');
  otherViews.forEach(v => v.classList.remove('active'));
  navs.forEach(n => n.classList.remove('active'));
  const homeNav = document.querySelector('.nav[data-home]');
  if(homeNav) homeNav.classList.add('active');
}

modes.forEach(btn => btn.addEventListener('click', () => showMode(btn.dataset.mode)));

document.querySelectorAll('[data-screen]').forEach(btn => {
  btn.addEventListener('click', () => {
    currentView.classList.remove('active');
    futureView.classList.remove('active');
    const target = document.querySelector(`.${btn.dataset.screen}-view`);
    if(target) target.classList.add('active');
    navs.forEach(n => n.classList.remove('active'));
    btn.closest('.nav')?.classList.add('active');
  });
});

document.querySelectorAll('[data-home]').forEach(btn => btn.addEventListener('click', () => {
  showMode('current');
}));

document.querySelectorAll('[data-help]').forEach(btn => btn.addEventListener('click', () => {
  currentView.classList.remove('active');
  futureView.classList.remove('active');
  otherViews.forEach(v => v.classList.remove('active'));
  const help = document.querySelector('.services-view');
  help.classList.add('active');
  navs.forEach(n => n.classList.remove('active'));
  btn.classList.add('active');
}));

serviceBacks.forEach(btn => btn.addEventListener('click', () => {
  showMode('current');
}));
