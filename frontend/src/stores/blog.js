// src/stores/blog.js
import { defineStore } from 'pinia'
import { blogService } from '@/services/blog.service'

export const useBlogStore = defineStore('blog', {
  state: () => ({
    posts: [],
    currentPost: null,
    loading: false,
    error: null,
    pagination: {
      page: 1,
      itemsPerPage: 10,
      totalItems: 0
    }
  }),

  getters: {
    sortedPosts: (state) => {
      return [...state.posts].sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      )
    }
  },

  actions: {
    async fetchPosts() {
      this.loading = true
      try {
        const response = await blogService.getPosts(
          this.pagination.page,
          this.pagination.itemsPerPage
        )
        this.posts = response.data
        this.pagination.totalItems = response.total
      } catch (error) {
        this.error = 'Erreur lors du chargement des articles'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createPost(postData, images) {
      this.loading = true
      try {
        const newPost = await blogService.createPost(postData, images)
        this.posts.unshift(newPost)
        return newPost
      } catch (error) {
        this.error = 'Erreur lors de la création de l\'article'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deletePost(postId) {
      try {
        await blogService.deletePost(postId)
        this.posts = this.posts.filter(post => post.id !== postId)
      } catch (error) {
        this.error = 'Erreur lors de la suppression de l\'article'
        throw error
      }
    }
  }
})
