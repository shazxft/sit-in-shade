const map = L.map('map',{zoomControl:true})
  .setView([20,0],2);

L.tileLayer(
 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
).addTo(map);

let route, m1, m2;

function setupAuto(input, box){
  input.oninput = async ()=>{
    box.innerHTML="";
    if(input.value.length<2) return;
    const res = await fetch(
      `https://photon.komoot.io/api/?q=${input.value}&limit=5`
    );
    const data = await res.json();
    data.features.forEach(f=>{
      const p=f.properties;
      if(!["city","state","country","county"].includes(p.type)) return;
      const name=[p.name,p.state,p.country].filter(Boolean).join(", ");
      const d=document.createElement("div");
      d.textContent=name;
      d.onclick=()=>{input.value=name;box.innerHTML="";}
      box.appendChild(d);
    })
  }
}

setupAuto(start,s1);
setupAuto(end,s2);

async function submitRoute(){
  const res = await fetch(
    `/shade-seat?start=${start.value}&end=${end.value}`
  );
  const d = await res.json();

  document.getElementById("panel").classList.add("move");

  if(route) map.removeLayer(route);
  if(m1) map.removeLayer(m1);
  if(m2) map.removeLayer(m2);

  m1=L.marker(d.start).addTo(map);
  m2=L.marker(d.end).addTo(map);

  route=L.polyline([d.start,d.end],{
    color:"#00ff00",weight:3
  }).addTo(map);

  map.fitBounds(route.getBounds(),{padding:[50,50]});

  result.innerHTML=
   `📏 Distance: ${d.distance} km<br>
    🌞 Sun on ${d.sun}<br>
    🪑 Best seat: <b>${d.seat}</b>`;
}

