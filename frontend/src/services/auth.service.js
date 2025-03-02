// src/services/auth.service.js
import api from './api'

export const authService = {
  async login(email, password) {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const response = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },

  async register(userData) {
    console.log('Register userData in service with detailed inspection:');
    // Inspecter l'objet File s'il existe
    if (userData.profile_image) {
      console.log('Profile image details:');
      console.log('- Name:', userData.profile_image.name);
      console.log('- Size:', userData.profile_image.size);
      console.log('- Type:', userData.profile_image.type);
    } else {
      console.log('No profile image provided');
    }
    
    // Créer un objet pour les données utilisateur sans l'image
    const userDataWithoutImage = {};
    for (const key in userData) {
      if (key !== 'profile_image' && key !== 'league') {
        userDataWithoutImage[key] = userData[key];
      }
    }
    
    // Gérer la ligue séparément
    if (userData.league) {
      userDataWithoutImage.league = userData.league;
    }
    
    console.log('User data being sent to API:', userDataWithoutImage);
    
    // Première requête : création de l'utilisateur
    const response = await api.post('/auth/register', userDataWithoutImage);
    
    // Se connecter automatiquement après l'inscription pour obtenir un token
    if (userData.email && userData.password) {
      try {
        console.log('Auto-login after registration...');
        const loginResponse = await this.login(userData.email, userData.password);
        
        // Stocker le token pour les requêtes suivantes
        localStorage.setItem('token', loginResponse.access_token);
        
        // Si une image est fournie, maintenant qu'on est authentifié, on peut l'envoyer
        if (userData.profile_image) {
          console.log('Uploading profile image after successful login');
          
          const formData = new FormData();
          formData.append('image', userData.profile_image);
          
          try {
            console.log('Posting image to API...');
            const imageResponse = await api.post('/users/profile/image', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });
            console.log('Profile image uploaded successfully:', imageResponse.data);
          } catch (imageError) {
            console.error('Error uploading profile image:', imageError);
            console.error('Error details:', imageError.response?.data);
          }
        }
      } catch (loginError) {
        console.error('Error logging in after registration:', loginError);
      }
    }

    return response.data;
  },

  async getProfile() {
    const response = await api.get('/users/profile')
    // Ajouter la gestion du cache pour l'image de profil
    if (response.data?.profile_image_path) {
      response.data.profile_image_path = `${response.data.profile_image_path}`
    }
    return response.data
  },

  async updateProfile(profileData) {
    // Séparation des données utilisateur et de l'image
    console.log('Données profileData:', profileData)

    //const { profile_image, ...userInfo } = userData
    //console.log('Données envoyées:', userInfo)

    const response = await api.put('/users/profile', profileData)

    return response.data
  },

  async uploadProfileImage(file) {
    console.log('uploadProfileImage called with:', file);
    
    const formData = new FormData()
    formData.append('image', file)
    
    const response = await api.post('/users/profile/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Détenteur actuel du jeton d'argile
  async getCurrentClayTokenHolder() {
    console.log('calling API:','/api/users/current-clay-token-holder')
    const response = await api.get('/users/current-clay-token-holder')
    console.log(response.data)
    return response.data
  },

  // Classement des chasseurs de prime
  async getBountyHuntersRanking(limit = 10) {
    const response = await api.get('/users/bounty-hunters', {
      params: { limit }
    })
    return response.data
  },

  async fetchUserStats(userId) {
    const response = await api.get(`/users/statistics/${userId}`)
    return response.data
  },

  // Historique du jeton d'argile
  async getClayTokenHistory(skip = 0, limit = 50) {
    const response = await api.get('/users/clay-token/history', {
      params: { skip, limit }
    })
    return response.data
  }
}