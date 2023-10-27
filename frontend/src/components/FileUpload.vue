<template>
  <div class="d-flex justify-content-center align-items-center" style="height: 50vh;">
    <div>
      <h1 class="mb-4">Upload de CSV</h1>
      <form @submit.prevent="uploadFile" enctype="multipart/form-data">
        <div class="mb-3">
          <input type="file" @change="onFileChange" class="form-control-file" accept=".csv" required>
        </div>
        <div class="d-flex justify-content-around mb-3 ml-3" >
          <button type="submit" class="btn btn-primary">Enviar</button>
          <router-link to="/lista" class="btn btn-success" >Rodovias Disponiveis</router-link>
        </div>
      </form>
      <!-- Mostra a mensagem de retorno do servidor como um alerta do Bootstrap -->
      <div class="mt-3">
        <div v-if="serverMessage" :class="alertClass">
          {{ serverMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      selectedFile: null,
      serverMessage: '', // Inicialmente vazia
    };
  },
  computed: {
    alertClass() {
      if (this.serverMessage === 'Upload feito com sucesso') {
        return 'alert alert-success';
      } else if (this.serverMessage === 'Erro no envio do arquivo') {
        return 'alert alert-danger';
      } else {
        return 'alert'; // Classe padrão
      }
    },
  },
  methods: {
    async uploadFile() {
      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        const response = await axios.post('http://127.0.0.1:8000/upload-csv/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        // Verifique a resposta do servidor
        if (response.status === 200) {
          this.serverMessage = 'Upload feito com sucesso';
        } else {
          this.serverMessage = 'Erro no envio do arquivo';
        }
      } catch (error) {
        console.error('Erro no envio do arquivo:', error);
        this.serverMessage = 'Erro no envio do arquivo';
      }
    },
    onFileChange(event) {
      this.selectedFile = event.target.files[0];
      // Limpe a mensagem ao selecionar um novo arquivo
      this.serverMessage = '';
    },
  },
};
</script>
