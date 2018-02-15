Vue.component('test-list-item', {
  props: [
	 "test"
  ],
  computed: {
	tagstring: function(){
		return this.test.tags.join(", ")
	}  
  },
  template: `
	  <div @click="navtodetail">
		  <div>
		  	<span>{{test.name}}</span>
		  	<span v-if="tagstring.length > 0">(tags: {{tagstring}})</span>  
		  </div>
		  <div v-if="test.description">
		  	<span>{{test.description}}</span>
		  </div>
	  </div>
  `,
  methods: {
	navtodetail()
	{
		this.$router.push("/test/" + this.test.name)
	}
  }
})