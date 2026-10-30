/* Adapted from Taster kit/motion.mjs. MIT — see TASTER-LICENSE.txt.
 * Classic-script wrapper supports offline file:// reading. */
(function () {
"use strict";
function createTransport({ duration, time=0, rate=1, loop=false }={}) {
  if(!Number.isFinite(duration)||duration<=0)throw new RangeError('duration must be positive seconds');
  let cursor=Math.max(0,Math.min(duration,time)),speed=rate,running=false;
  if(!Number.isFinite(speed)||speed===0)throw new RangeError('rate must be finite and nonzero');
  const snapshot=()=>({time:cursor,progress:cursor/duration,duration,rate:speed,playing:running});
  const seek=value=>{if(!Number.isFinite(value))throw new TypeError('seek expects finite seconds');cursor=Math.max(0,Math.min(duration,value));return snapshot();};
  return {
    getState:snapshot,
    play(){ if((speed>0&&cursor===duration)||(speed<0&&cursor===0))cursor=speed>0?0:duration;running=true;return snapshot(); },
    pause(){running=false;return snapshot();},
    toggle(){return running?this.pause():this.play();},
    seek,
    step(seconds){running=false;return seek(cursor+seconds);},
    setRate(value){if(!Number.isFinite(value)||value===0)throw new RangeError('rate must be finite and nonzero');speed=value;return snapshot();},
    update(dt){
      if(!running||!Number.isFinite(dt)||dt<=0)return snapshot();
      const next=cursor+dt*speed;
      if(loop)cursor=((next%duration)+duration)%duration;
      else {cursor=Math.max(0,Math.min(duration,next));if(next>=duration||next<=0)running=false;}
      return snapshot();
    },
  };
}

window.Taster = Object.freeze({ createTransport });
})();
