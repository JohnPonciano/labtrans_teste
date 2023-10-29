<template>
  <div class="container">
    <h1>Rodovia {{ internalValue }}</h1>
    <div class="row mb-3">
      <div class="col-md-6">
        <input
          v-model="internalValue"
          @input="updateParent"
          type="text"
          class="form-control"
          placeholder="Digite a Highway"
        />
      </div>
      <div class="col-md-2">
        <button @click="filterItems" class="btn btn-primary">Filtrar</button>
      </div>
    </div>
    <div class="row">
      <div class="col-lg-12">
        <div id="map"></div>
      </div>
    </div>

    <!-- Adicione uma div para a tela de carregamento -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loader"></div>
      <p>Consultando...</p>
    </div>
  </div>
</template>

<script>
 /* eslint-disable */
import L from "leaflet";

export default {
  props: {
    highwayInput: Number,
  },
  data() {
    return {
      internalValue: this.highwayInput,
      map: null,
      allLayers: {},
      isLoading: false,
    };
  },
  watch: {
    internalValue(newVal) {
      this.$emit("input", newVal);
    },
  },
  mounted() {
    // Inicialização do mapa
    if (!this.map) {
      this.map = L.map("map",{zoomControl: true,zoom:1,zoomAnimation:false,fadeAnimation:true,markerZoomAnimation:true}).setView([0, 0], 2);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
          'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 18,
      }).addTo(this.map);
    }

    this.addMarkersForHighway(); // Carrega marcadores na montagem do mapa

    // Manipulador para evento de zoom - aqui você pode tentar corrigir o possível erro de zoom
    this.map.on("zoomend", () => {
      // Qualquer lógica que você esteja utilizando ao manipular o zoom
      // Certifique-se de estar usando a instância de mapa correta e evite acessar valores nulos
      console.log("Zoom Out: ", this.map.getZoom());
    });
    this.map.on("zoomstart", () => {
      // Qualquer lógica que você esteja utilizando ao manipular o zoom
      // Certifique-se de estar usando a instância de mapa correta e evite acessar valores nulos
      console.log("Zoom In: ", this.map.getZoom());
    });
  },

  methods: {
    updateParent() {
      this.$emit("input", this.internalValue);
    },

    addMarkersForHighway() {
      this.isLoading = true;

      fetch(`http://127.0.0.1:8000/all-rows/${this.internalValue}`)
        .then((response) => response.json())
        .then((data) => {
          const allRows = data.all_rows;

          if (this.controlLayers) {
            this.map.removeControl(this.controlLayers);
          }

          for (const key in this.allLayers) {
            if (Object.prototype.hasOwnProperty.call(this.allLayers, key)) {
              const layer = this.allLayers[key];
              if (layer) {
                layer.clearLayers();
              }
            }
          }

          for (const row of allRows) {
            const popupContent = 
            `Rodovia: ${row.highway}
            <br> id:${row.id}
            <br> Item: ${row.item} 
            <br> Long: ${row.longitude} 
            <br> Lat: ${row.latitude} `;
            if (!this.allLayers[row.item]) {
              this.allLayers[row.item] = L.layerGroup().addTo(this.map);
            }
            const marker = L.marker([
              parseFloat(row.latitude),
              parseFloat(row.longitude),
            ])
              .addTo(this.allLayers[row.item])
              .bindPopup(popupContent)
          }

          this.isLoading = false;

          // Add a control to toggle layers
          this.controlLayers = L.control
            .layers(null, this.allLayers)
            .addTo(this.map);
        })
        .catch((error) => {
          console.error("Error:", error);
          this.isLoading = false;
        });
    },

    filterItems() {
      // Call addMarkersForHighway without passing highwayInput
      this.addMarkersForHighway();
    },
  },
};
</script>

<style>
#map {
  height: 400px;
}

/* Estilos para a tela de carregamento */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
