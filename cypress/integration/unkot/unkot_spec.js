const now = new Date().getTime()
const email =  'test_email_' + now + '@example.com'
const userName = 'TestUser-' + now
const userPassword = 'Test user pass 123!'

// set new user email as verified using test-admin account
const adminUser = Cypress.env('adminUser')
const adminPassword = Cypress.env('adminPassword')
expect(adminUser, 'adminUser was set').to.be.a('string').and.not.be.empty
if (typeof adminPassword !== 'string' || !adminPassword) {
  throw new Error('Missing adminPassword value, set it in cypress.env.json.')
}

describe('Register as new user', () => {
  // TODO save new search without subscribing the search, add deed matching the search, verify no email notification is sent
  // TODO save new search and subscribe the search, add deed matching the search, verify the notification is sent

	it('clik the sign up ink', () => {
		cy.visit('/')
    cy.get('#sign-up-link').click()
    cy.url().should('include', '/accounts/signup/')
  })

  it('fill out and submit registration form', () => {
    cy.visit('/accounts/signup/')

    cy.get('#id_email')
      .type(email)
      .should('have.value', email)
    cy.get('#id_username')
      .type(userName)
      .should('have.value', userName)
    cy.get('#id_password1')
      .type(userPassword)
      .should('have.value', userPassword)
    cy.get('#id_password2')
      .type(userPassword)
      .should('have.value', userPassword)
    cy.get('button[class="btn btn-primary"][type="submit"]').click()
    cy.url().should('include', '/accounts/confirm-email')
  })

  it('mark test user email as verified', () => {
    cy.visit('/')
    cy.get('#log-in-link').click()
    cy.get('#id_login')
      .type(adminUser)
      .should('have.value', adminUser)
    cy.get('#id_password')
      .type(adminPassword)
      .should('have.value', adminPassword)
    cy.get('.primaryAction').click()
    cy.visit('/admin/account/emailaddress/')
    cy.contains(email).click()
    cy.get('#id_verified').click()
    cy.get('input[name=_save]').click()
    cy.visit('/admin/logout/')
  })

  it('log in and log out as existing user', () => {
		cy.visit('/')
    cy.get('#log-in-link').click()
    cy.get('#id_login')
      .type(userName)
      .should('have.value', userName)
    cy.get('#id_password')
      .type(userPassword)
      .should('have.value', userPassword)
    cy.get('.primaryAction').click()
    cy.url().should('include', userName)

    // FIXME add here tests using logged in user

    cy.visit('/isap/')
    cy.visit('/accounts/logout/')
    cy.get('button[class="btn btn-danger"').click()
    cy.visit('/')
    cy.get('#log-in-link')
  })

  it('remove existing user using test-admin account', () => {
    cy.visit('/')
    cy.get('#log-in-link').click()
    cy.get('#id_login')
      .type(adminUser)
      .should('have.value', adminUser)
    cy.get('#id_password')
      .type(adminPassword)
      .should('have.value', adminPassword)
    cy.get('.primaryAction').click()
    cy.visit('/admin/users/user/')
    cy.contains(userName).click()
    cy.get('.deletelink').click()
    cy.url().should('include', '/delete/')
    cy.get('input[type=submit]').click()
    cy.visit('/')
  })
})
