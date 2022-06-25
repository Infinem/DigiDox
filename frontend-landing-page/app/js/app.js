// // Import vendor jQuery plugin example
// import '~/app/libs/mmenu/dist/mmenu.js'


document.addEventListener('DOMContentLoaded', () => {
	var dataReload = document.querySelectorAll("[data-reload]")
	console.log(dataReload)
	var lang = {
		uz: {
			greeting: "Salom"
		},
		ru: {
			greeting: "Привет"
		}
	}

	if (window.location.hash) {
		if (window.location.hash === "#ru") {
			hi.textContent = lang.ru.greeting
		}
	}

	for (let i = 0; i <= dataReload.length; i++) {
		console.log("inside")
		console.log(dataReload[i])
		dataReload.onclick = function () {
			location.reload(true);
		}
	}

	const links = document.querySelectorAll(".page-header ul a");

	for (const link of links) {
		link.addEventListener("click", clickHandler);
	}

	function clickHandler(e) {
		e.preventDefault();
		const href = this.getAttribute("href");
		const offsetTop = document.querySelector(href).offsetTop -120;

		scroll({
			top: offsetTop,
			behavior: "smooth"
		});
	}

	// $("a").on('click', function (event) {

	// 	// Make sure this.hash has a value before overriding default behavior
	// 	if (this.hash !== "") {
	// 		// Prevent default anchor click behavior
	// 		event.preventDefault();

	// 		// Store hash
	// 		var hash = this.hash;

	// 		// Using jQuery's animate() method to add smooth page scroll
	// 		// The optional number (800) specifies the number of milliseconds it takes to scroll to the specified area
	// 		$('html, body').animate({
	// 			scrollTop: $(hash).offset().top
	// 		}, 800, function () {

	// 			// Add hash (#) to URL when done scrolling (default click behavior)
	// 			window.location.hash = hash;
	// 		});
	// 	} // End if
	// });

})
