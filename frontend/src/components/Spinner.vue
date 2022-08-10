<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div class=" spinner sl-spinner" v-show="status" :style="spinnerStyle"></div>
</template>

<script lang="ts">
  import Component from 'vue-class-component';
  import Vue from 'vue';
  import {mapActions, mapGetters} from "vuex";

  @Component({
    props: {
      status: {
        type: Boolean,
        default: true
      },

      rotation: {
        type: Boolean,
        default: true
      },

      size: {
        type: Number,
        default: 80
      },

      depth: {
        type: Number,
        default: 3
      },

      speed: {
        type: Number,
        default: 1.0
      },

      color: {
        type: String,
        default: '#6589b6'
      }
    },
  })
  export default class Spinner extends Vue {
    rotationAnimations: string[] = ['forward', 'backward'];
    sizeUnits:string = 'px';
    timeUnits:string = 's';
    // declare in component decorators
    status!:boolean;
    rotation!:boolean;
    size!:number;
    depth!:number;
    speed!:number;
    color!:string;



    get rotationDirection() {
      return this.rotation ? this.rotationAnimations[0] : this.rotationAnimations[1];
    }

    get spinnerSize() {
      return this.size + this.sizeUnits;
    }

    get spinnerDepth() {
      return this.depth + this.sizeUnits;
    }

    get spinnerSpeed() {
      return this.speed + this.timeUnits;
    }

    get spinnerStyle() {
      return {
        borderTopColor: this.hexToRGB(this.color, 0.15),
        borderRightColor: this.hexToRGB(this.color, 0.15),
        borderBottomColor: this.hexToRGB(this.color, 0.15),
        borderLeftColor: this.color,
        width: this.spinnerSize,
        height: this.spinnerSize,
        borderWidth: this.spinnerDepth,
        animationName: this.rotationDirection,
        animationDuration: this.spinnerSpeed
      }
    }

    hexToRGB(hex:string, alpha:number) {
      var r = parseInt(hex.slice(1, 3), 16),
              g = parseInt(hex.slice(3, 5), 16),
              b = parseInt(hex.slice(5, 7), 16);

      if (alpha) {
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
      } else {
        return `rgb(${r}, ${g}, ${b})`;
      }
    }
  }
</script>

<style lang="scss">

  .sl-spinner {
    border-style: solid;
    -webkit-transform: translateZ(0);
    -ms-transform: translateZ(0);
    transform: translateZ(0);

    animation-iteration-count: infinite;
    animation-timing-function: linear;

    border-radius: 50%;
    width: 30px;
    height: 30px;
  }

  @keyframes forward {

      0% {
        -webkit-transform: rotate(0deg);
        transform: rotate(0deg);
      }

      100% {
        -webkit-transform: rotate(360deg);
        transform: rotate(360deg);
      }

  }

  @keyframes backward {

    0% {
      -webkit-transform: rotate(0deg);
      transform: rotate(0deg);
    }

    100% {
      -webkit-transform: rotate(360deg);
      transform: rotate(-360deg);
    }

  }

</style>