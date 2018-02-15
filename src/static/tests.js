var Tests = Vue.component('tests', {
  template: `
    <div>
	  <p>Search: <input v-model="searchtext" placeholder="test name or tags"></p>
	  <ul>
		  <li v-for="test in tests">
		  	<test-list-item :test="test" />
		  </li>
	  </ul>
	</div>
  `,
  data: function() 
  {
	  return {
	    alltests: [],
		searchtext: ""
	  }
  },
  created: function () {
	  this.getTests()
  },
  computed: {
	tests: function() 
	{
		if (!this.searchtext)
		{
			return this.alltests
		}
		else
		{
			var searchelems = this.searchtext.split(" ");
			return _.filter
			(
				this.alltests,
				function(test) 
				{ 
					var matches = _.filter(
						searchelems,
						function(item) {
							return item && 
								(
									(test.name.search(item) >= 0) ||
									(
										_.filter
										(
											test.tags,
											function(tag)
											{
												return tag && tag.search(item) >= 0;
											}
										).length > 0
									)
								);
						}
					);
					
					return matches.length > 0;
				}
			);
		}
	}
  },
  methods: {
    getTests() 
    {
      this.$http.get('/megatest/tests').then(
        function (response) 
	    {
	      this.alltests = response.data;
	    }
      );
    }
  }
})