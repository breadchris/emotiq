boomsvgloader.load('/static/images/icons/icon-sprite.svg');

var searchToggle = document.querySelector('.search-toggle');
var searchForm = document.querySelector('.search-form');

function toggleSearch() {
	searchForm.classList.toggle('open');
	searchToggle.classList.toggle('flipped');
}

searchToggle.addEventListener('click', toggleSearch);


/* Random Placeholder */
var placeholders = [
    "msft",
    "aapl",
	"goog",
	"Clinton",
	"Trump",
	"coal",
	"tsla",
	"solar",
	"sbux"
];

function changePlaceholder() {
	var current_placeholder = placeholders[Math.floor(Math.random() * placeholders.length)];

	document.querySelector('input[type="search"]').placeholder = current_placeholder;
}

window.setInterval(function(){
	changePlaceholder();
}, 5000);