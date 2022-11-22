
const INTERVAL = 6000


function update(){
// 	fetch('http://0.0.0.0:5000')
  // .then((response) => response.json())
  // .then((data) => {
  	
  // });

}


function main(){
	window.setInterval(update(),INTERVAL);
}


document.addEventListener('DOMContentLoaded',main());