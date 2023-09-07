function closeMenu() {
  let input = document.getElementById('checkbox_toggle');
  input.checked = false;
}


$(window).scroll(function() {
    if ($(window).scrollTop() > 10) {
        $("nav").addClass('floatingNav');
    } else {
        $("nav").removeClass('floatingNav');
    }
});

const sections = document.querySelectorAll("section");
const navLi = document.querySelectorAll("nav ul li");
window.onscroll = () => {
  var current = "";

  sections.forEach((section) => {
    const sectionTop = section.offsetTop;
    if (scrollY >= sectionTop - 60) {
      current = section.getAttribute("id"); }
  });

  navLi.forEach((li) => {
    li.classList.remove("active");
    if (li.classList.contains(current)) {
      li.classList.add("active");
    }
  });
};


jQuery(document).ready(function($){
	$('.popup-trigger').on('click', function(event){
		event.preventDefault();
		$('.popup').addClass('is-visible');
	});
	

	$('.popup').on('click', function(event){
		if( $(event.target).is('.popup-close') || $(event.target).is('.popup') ) {
			event.preventDefault();
			$(this).removeClass('is-visible');
		}
	});


  $(document).keyup(function(event){
    	if(event.which=='27'){
    		$('.popup').removeClass('is-visible');
	    }
    });
});

