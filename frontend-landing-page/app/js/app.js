// // Import vendor jQuery plugin example
// import '~/app/libs/mmenu/dist/mmenu.js'


document.addEventListener('DOMContentLoaded', () => {
	// const langs = document.querySelectorAll(".lang");
	// const langsLinks = document.querySelectorAll(".lang-link");

	// if (window.location.hash && window.location.hash === "#uz") {
	// 	langs.forEach(elem => {
	// 		elem.textContent = elem.dataset.uz;
	// 	});
	// }

	// langsLinks.forEach(elem => {
	// 	elem.onclick = function () {
	// 		console.log(elem)
	// 		window.location.reload(true);
	// 	};
	// });

	const links = document.querySelectorAll(".page-header ul a");

	for (const link of links) {
		link.addEventListener("click", clickHandler);
	}

	function clickHandler(e) {
		e.preventDefault();
		const href = this.getAttribute("href");
		const offsetTop = document.querySelector(href).offsetTop - 120;

		scroll({
			top: offsetTop,
			behavior: "smooth"
		});
	}


})
