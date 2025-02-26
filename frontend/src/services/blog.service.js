// src/services/blog.service.js
import api from './api'

export const blogService = {
  async getPosts(page = 1, limit = 10) {
    const response = await api.get('/blog/', {
      params: { page, limit }
    })
    return response.data
  },

  async getPost(id) {
    const response = await api.get(`/blog/${id}`)
    return response.data
  },

  async createPost(postData) {
    const formData = new FormData()
    
    // Ajout du titre et du contenu
    formData.append('title', postData.title)
    formData.append('content', postData.content)
    
    // Ajout des images s'il y en a
    if (postData.images) {
      postData.images.forEach((image, index) => {
        formData.append(`images`, image)
      })
    }

    const response = await api.post('/blog/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async updatePost(id, postData) {
    const formData = new FormData()
    
    formData.append('title', postData.title)
    formData.append('content', postData.content)
    
    if (postData.images) {
      postData.images.forEach((image, index) => {
        if (image instanceof File) {
          formData.append(`new_images`, image)
        } else {
          formData.append(`existing_images`, image)
        }
      })
    }

    const response = await api.put(`/blog/${id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async deletePost(id) {
    const response = await api.delete(`/blog/${id}`)
    return response.data
  },

  async addImages(postId, images) {
    const formData = new FormData()
    images.forEach((image, index) => {
      formData.append(`images`, image)
    })

    const response = await api.post(`/blog/${postId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }
}