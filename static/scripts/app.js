boomsvgloader.load('/static/images/icons/icon-sprite.svg');

var searchToggle = document.querySelector('.search-toggle');
var searchForm = document.querySelector('.search-form');

function toggleSearch() {
	searchForm.classList.toggle('open');
	searchToggle.classList.toggle('flipped');
}

searchToggle.addEventListener('click', toggleSearch);