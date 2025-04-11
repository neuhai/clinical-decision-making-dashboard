<template>
    <div ref="gaugeContainer">
      <p>
        <small>
          <center>{{ title }}</center>
        </small>
      </p>
      <vue-gauge
        :refid="'_' + Math.random().toString(36).substr(2, 9)"
        :options="myOptions"
      />
    </div>
  </template>
  
  <script>
  import VueGauge from "vue-gauge";
  
  export default {
    components: { VueGauge },
    props: {
      title: String,
      value: Number, // Ensure this is a number to work with calculations in data
    },
    data() {
      return {
        myOptions: {
          chartWidth: 200, // Fixed width for consistent sizing
          needleValue: this.value / 0.6,
          needleColor: "black",
          arcDelimiters: [15 / 0.6, 40 / 0.6],
          arcColors: ["rgb(61,204,91)", "rgb(239,214,19)", "rgb(255,84,84)"],
          arcLabels: ["15", "40"],
          rangeLabel: ["0", "100"], // Adjusted to better match your use case
          centralLabel: `${this.value}%`,
          rangeLabelFontSize: 14,
        },
      };
    },
    watch: {
      value(newValue) {
        // Dynamically update the gauge when the value prop changes
        this.myOptions.needleValue = newValue / 0.6;
        this.myOptions.centralLabel = `${newValue}%`;
      },
    },
    mounted() {
      console.log("Gauge component mounted.");
    },
  };
  </script>
  
  <style scoped>
  #gaugeContainer {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  </style>
  
  