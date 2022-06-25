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

	for (let i = 0; i <= dataReload.length ; i++) {
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
		const offsetTop = document.querySelector(href).offsetTop;

		scroll({
			top: offsetTop,
			behavior: "smooth"
		});
	}

})
