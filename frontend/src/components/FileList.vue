<template>
  <div>
    <!-- Parte Superior: Título e Menu de Dropdown -->
    <div class="container">
      <h1 class="display-4 mt-4">Rodovias Disponíveis</h1>
      <div class="form-group mt-4">
        <label for="incidenceDropdown">Selecione a Incidência:</label>
        <select
          v-model="selectedIncidence"
          @change="handleIncidenceChange"
          class="form-control"
          id="incidenceDropdown"
        >
          <option value="todos">Todos</option>
          <option value="buraco">Buraco</option>
          <option value="remendo">Remendo</option>
          <option value="trinca">Trinca</option>
          <option value="placa">Placa</option>
          <option value="drenagem">Drenagem</option>
        </select>
      </div>
    </div>
    <div class="container container-fluid mt-4">
      <!-- Parte do Meio: Grids de Arquivos -->
      <div class="row">
        <div
          v-for="item in sortedFileList"
          :key="item.highway"
          class="col-md-4"
        >
          <div class="card mb-4">
            <div class="card-body d-flex justify-content-between">
              <a
                href="#"
                @click="downloadFile(item.highway)"
                class="btn btn-primary btn-block mb-2"
                >{{ `Download Rodovia - ${item.highway}` }}</a
              >
              <button
                @click="showDetails(item.highway)"
                class="btn btn-info btn-block mb-2"
              >
                Detalhes
              </button>
            </div>
            <div class="card-body d-flex justify-content-between">
              <button
                @click="openMapModal(item.highway)"
                class="btn btn-success btn-block mb-2"
              >
                Visualizar Mapa
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Parte Inferior: Modal para exibir detalhes -->
      <div
        v-if="selectedHighway"
        class="modal fade show"
        style="display: block"
      >
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h2 class="modal-title">
                Detalhes da Rodovia {{ selectedHighway }}
              </h2>
              <button
                type="button"
                class="btn-close"
                @click="closeDetails"
              ></button>
            </div>
            <div class="modal-body">
              <p>Km_exp: {{ highwayDetails.km_exp }}</p>
              <p>Km: {{ highwayDetails.Km }}</p>
              <p>Buraco: {{ highwayDetails.buraco }}</p>
              <p>Remendo: {{ highwayDetails.remendo }}</p>
              <p>Trinca: {{ highwayDetails.trinca }}</p>
              <p>Placa: {{ highwayDetails.placa }}</p>
              <p>Drenagem: {{ highwayDetails.drenagem }}</p>
            </div>
          </div>
        </div>
      </div>

     <!-- Modal para exibir o mapa -->
    <div v-if="showMapModal" class="modal " style="display: block;">
      <div class="modal-dialog"  >
        <div class="modal-content" >
          <div class="modal-header">
            <h5 class="modal-title">Mapa da Rodovia {{ selectedHighway }}</h5>
            <button @click="closeMapModal" type="button" class="btn-close"></button>
          </div>
          <div class="modal-body">
            <!-- Carrega o componente LMap.vue com a prop "highwayNumber" -->
            <LMap :highwayInput="selectedHighway" />
          </div>
        </div>
      </div>
    </div>


  </div>
  </div>
</template>

<script>
import LMap from './LMap.vue'; // Importe o componente LMap.vue

export default {
  components: {
    LMap // Registre o componente LMap
  },
  data() {
    return {
      fileList: [],
      selectedHighway: null,
      highwayDetails: {},
      selectedIncidence: 'todos',
      showMapModal: false,
    };
  },
  computed: {
    sortedFileList() {
      return this.fileList
        .slice()
        .sort((a, b) => b[this.selectedIncidence] - a[this.selectedIncidence]);
    },
  },
  mounted() {
    this.fetchHighwaysData();
  },
  methods: {
    fetchHighwaysData() {
      fetch("http://127.0.0.1:8000/list-highways")
        .then((response) => response.json())
        .then((data) => {
          this.fileList = data;
        })
        .catch((error) => {
          console.error("Erro ao obter os dados da API:", error);
        });
    },
    showDetails(highwayNumber) {
      fetch(`http://127.0.0.1:8000/list-highways/${highwayNumber}`)
        .then((response) => response.json())
        .then((data) => {
          this.highwayDetails = data[0];
          this.selectedHighway = highwayNumber;
        })
        .catch((error) => {
          console.error("Erro ao obter os detalhes da rodovia:", error);
        });
    },
    closeDetails() {
      this.selectedHighway = null;
      this.highwayDetails = {};
    },
    downloadFile(highwayNumber) {
      fetch(`http://127.0.0.1:8000/export-csv/${highwayNumber}`)
        .then((response) => response.blob())
        .then((blob) => {
          const url = window.URL.createObjectURL(new Blob([blob]));
          const a = document.createElement("a");
          a.href = url;
          a.download = `Highway_${highwayNumber}.csv`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
        })
        .catch((error) => {
          console.error("Erro ao fazer o download do arquivo:", error);
        });
    },

    // Abre o modal e define a rodovia selecionada
    openMapModal(highwayNumber) {
      this.selectedHighway = highwayNumber; // Defina a rodovia selecionada
      this.showMapModal = true; // Abre o modal
    },
    // Fecha o modal
    closeMapModal() {
      this.selectedHighway = null; // Limpa a rodovia selecionada ao fechar o modal
      this.showMapModal = false; // Fecha o modal
    },
  }
};
</script>
