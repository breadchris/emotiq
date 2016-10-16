boomsvgloader.load('/static/images/icons/icon-sprite.svg');

document.addEventListener( 'DOMContentLoaded', function() {
	
	var elem = document.querySelector('.articles');
	
	// Setup Masonry.
	var msnry = new Masonry( elem, {
		itemSelector: '.article',
		transitionDuration: 0
	});
	
	imagesLoaded( elem ).on( 'progress', function() {
		// Layout Masonry after each image loads.
		msnry.layout();
	});

});