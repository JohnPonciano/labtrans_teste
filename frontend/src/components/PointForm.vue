<template>
  <div>
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label for="pointId" class="form-label">ID do Ponto:</label>
        <input type="number" class="form-control" v-model="pointId" id="pointId" />
      </div>
      <div class="mb-3">
        <label for="latitude" class="form-label">Latitude:</label>
        <input type="text" class="form-control" v-model="latitude" id="latitude" />
      </div>
      <div class="mb-3">
        <label for="longitude" class="form-label">Longitude:</label>
        <input type="text" class="form-control" v-model="longitude" id="longitude" />
      </div>
      <button type="submit" class="btn btn-primary">Salvar</button>
    </form>

    <div v-if="successMessage" class="alert alert-success mt-3" role="alert">
      {{ successMessage }}
    </div>

    <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      pointId: null,
      latitude: '',
      longitude: '',
      successMessage: '',
      errorMessage: ''
    };
  },
 methods: {
    handleSubmit() {
      if (this.pointId && this.latitude && this.longitude) {
        fetch(`http://127.0.0.1:8000/point/${this.pointId}?latitude=${this.latitude}&longitude=${this.longitude}`, {
          method: 'PUT'
        })
          .then(response => {
            if (response.ok) {
              this.successMessage = 'Ponto atualizado com sucesso';
              this.errorMessage = ''; // Limpa a mensagem de erro se houver
            } else {
              throw new Error('Não foi possível atualizar o ponto');
            }
          })
          .catch(error => {
            this.errorMessage = error.message;
            this.successMessage = ''; // Limpa a mensagem de sucesso se houver
          });
      } else {
        this.errorMessage = 'Por favor, preencha todos os campos';
        this.successMessage = ''; // Limpa a mensagem de sucesso se houver
      }
    }
  }
};
</script>
