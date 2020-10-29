var slideIndex = 0;
showSlides();
showSlides();
showSlides();
showSlides();
showSlides();
showSlides();
function showSlides() {
  var i;
  var slides = document.getElementsByClassName("mySlides fade");
  var dots = document.getElementsByClassName("dot");
  for (i = 0; i < slides.length; i++) {  //slides.length
    slides[i].style.display = "none";  
  }
  slideIndex++;
  if (slideIndex > slides.length) {slideIndex = 1}    
  for (i = 0; i < dots.length; i++) {  //dots.length
    dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";  
  dots[slideIndex-1].className += " active";
  setTimeout(showSlides, 2000); // Change image every 2 seconds
}