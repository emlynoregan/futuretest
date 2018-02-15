const routes = [
  { path: '/', component: Tests },
  { path: '/test/:testname', component: Test, props: true }
]

const router = new VueRouter({
	  routes // short for `routes: routes`
	})

var app = new Vue({
  el: '#app',
  data: {
    message: 'Megatest'
  },
  router
});