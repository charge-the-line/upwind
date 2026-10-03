// Independent recalculation of zone fit. Written from the rules in CLAUDE.md, not from the app's zoneFit, so the two can disagree.
// A fit is good when: hot ring >= 95% of the ERG isolation distance and <= 2.5x it; warm ring >= hot + 40 ft;
// staging within 60 degrees of straight upwind and at least the warm radius away from the release point.
function expected(z,windDeg,isoFt,R,ftPerPx){const notes=[];let pen=0;
  if(z.hot<isoFt*0.95){notes.push('hot short');pen+=10;}else if(z.hot>isoFt*2.5){notes.push('hot huge');pen+=5;}
  if(z.warm<z.hot+40){notes.push('warm thin');pen+=5;}
  // upwind unit vector on screen: compass 0 = up (negative y), 90 = right
  const rad=windDeg*Math.PI/180,ux=Math.sin(rad),uy=-Math.cos(rad);const dx=z.stage.x-R.x,dy=z.stage.y-R.y,len=Math.hypot(dx,dy)||1;
  const cosang=(dx*ux+dy*uy)/len;if(cosang<0.5){notes.push('not upwind');pen+=10;}
  // distance is judged in whole feet, the number the player sees on screen
  if(Math.round(len*ftPerPx)<z.warm){notes.push('inside warm');pen+=10;}
  return {ok:pen===0,pen,notes};}
module.exports={expected};
