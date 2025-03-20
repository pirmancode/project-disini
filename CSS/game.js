const jenis = [

  {
    pesawat1: "planec2.jpg",
    pesawat2: "planec2.png",
  },
  {
    pesawat1: "planed1.png",
    pesawat2: "planed2.png",
  },
];
var kecepatanLatar = 2;
var kecepatanMeteor = 4;
var kecepatanammo = 10;

let score = document.getElementById("score");
let angkascore = 0;

var meteor = document.getElementById("meteor");

const pesawat = document.getElementById("plane");
const ammo = document.getElementById("ammo");
const ufo = document.getElementById("ufo")
const nyawa = document.querySelector(".nyawa")

const next = document.getElementById("next");
const back = document.getElementById("back");

const startpage = document.querySelector(".startpage")

const story = document.getElementById("story")
const storyimg = document.getElementById("storyimg")
const storyskip = document.getElementById("skip")

let arena = document.querySelector("main")

const start = document.getElementById("start");
let maju = false;



let pesawaty = 30


let nopesawat = 0;

next.addEventListener("click", function () {
  nopesawat++;

  if (nopesawat == jenis.length) {
    nopesawat = 0;
  }
  console.log(nopesawat);
  pesawat.style.backgroundImage = `url(images/${jenis[nopesawat].pesawat2})`;

  return nopesawat;
});

back.addEventListener("click", function () {
nopesawat--;
  if (nopesawat < 0) {
    nopesawat = jenis.length -1
  }
  console.log(nopesawat)
  pesawat.style.backgroundImage = `url(images/${jenis[nopesawat].pesawat2})`;

});


start.addEventListener("click", function () {
  startstory()
});

//type writer
function startstory(){
    startpage.style.animation = "hilang 1s"
    setTimeout(() => {
        startpage.style.visibility = "hidden";
    }, 1000);
    setTimeout(() => {
        storyimg.style.animation = "kanan 2s"
        story.style.display = "block"
        var app = document.getElementById('app');
        var typewriter = new Typewriter(app, {
            loop: false
        });
    
        typewriter.typeString('Hello Player selemat di Spacearound')
            .pauseFor()
            .deleteAll()
            .typeString('Bersiaplah untuk memulai petualangan yang luar biasa')
            .pauseFor(1000)
            .deleteAll()
            .typeString('waspada musuh terlihat !!!')
            .pauseFor(1000)
            .start();
    }, 1000);
    


}

storyskip.addEventListener("click",function(){
    story.style.display = "none"
    startgame();
    setbggerak(); 
    ufo.style.animation = "kabur 3s"
    setTimeout(() => {
      ufo.style.visibility= "hidden"
      nyawa.style.visibility= "visible"
      setmeteor();  
    }, 3000);
})

function startgame(){
    maju = true

    arena.style.animation = "muncul 1s"
    arena.style.visibility = "visible"
    setTimeout(() => {
      pesawat.style.position = "absolute"
      pesawat.style.animation = "pesawatmuncul 1s"
      pesawat.style.visibility = "visible"
      pesawat.style.bottom = pesawaty + "px"  
      
    }, 2000);


    return maju
}

function setbggerak() {
 
  if (maju) {
    setTimeout(function () {

      arena.style.backgroundPositionY =
            parseInt(arena.style.backgroundPositionY.replace("px", "")) +
            kecepatanLatar +
            "px";
      arena.style.backgroundPositionX =
            parseInt(arena.style.backgroundPositionX.replace("px", "")) +
            kecepatanLatar +
            "px";
        setbggerak('');
    }, 5);
  }
}

function setmeteor(){

  setTimeout(() => {
    var point = 0

    kecepatanMeteor += 2;
    meteor.style.marginTop = kecepatanMeteor + "px";
    if (parseInt(meteor.style.marginTop) > 800) {
      meteor.style.marginLeft = Math.floor(Math.random() * 250) + 50 + "px";
      kecepatanMeteor = 0
      point++
    }

    if (cekTabrakan(meteor, pesawat)) {
      maju = false
        gameOver();
      return;
    }
    
    setmeteor();
  }, 5);
}



function cekTabrakan(meteor, pesawat) {
  const rectMeteor = meteor.getBoundingClientRect();
  const rectRoket = pesawat.getBoundingClientRect();

  return (
    rectMeteor.top + 105 >= rectRoket.top &&
    rectMeteor.left + 90 >= rectRoket.left &&
    rectMeteor.top + 105 <= rectRoket.top + 85 &&
    rectMeteor.left <= rectRoket.left + 50
  );
}

const lose = document.getElementById("gameover");
function gameOver(){
  lose.style.animation = "muncul 2s"
  lose.style.visibility = "visible"

}

window.addEventListener("keydown",function(e){
  if(maju){
    posisix = parseInt(pesawat.style.marginLeft)
    console.log(posisix)
    if(e.keyCode == 37 && posisix > -360){
      pesawat.style.marginLeft = posisix - 30 + "px"
      ammo.style.marginLeft = posisix - 30 + "px"
    }
    if(e.keyCode == 39 && posisix < 360){
      pesawat.style.marginLeft = posisix + 30 + "px"
      ammo.style.marginLeft = posisix + 30 + "px"
    }
    if(e.keyCode == 38){
      ammo.style.visibility = "visible"
      ammo.style.animation = "ammo 1s"
      setTimeout(() => {
        ammo.style.visibility = "hodden"
        ammo.style.animation = "none"
      }, 1000);
    }
  }
})


document.getElementById("restart").addEventListener("click", function(){
  pesawat.style.position = "static"
  pesawat.style.margin = "0"
   arena.style.visibility = "hidden"
  lose.style.visibility = "hidden"
  startpage.style.visibility = "visible";

})