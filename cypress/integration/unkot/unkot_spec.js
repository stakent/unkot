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

	it('clik the link "Załóż nowe konto"', () => {
		cy.visit('/')
    cy.contains('Załóż nowe konto').click()
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
    cy.contains('Załóż nowe konto »').click()
    cy.contains('Proszę zweryfikować Państwa adres e-mail')
  })

  it('mark test user email as verified', () => {
    cy.visit('/')
    cy.contains('Zaloguj').click()
    cy.get('#id_login')
      .type(adminUser)
      .should('have.value', adminUser)
    cy.get('#id_password')
      .type(adminPassword)
      .should('have.value', adminPassword)
    cy.get('.primaryAction').click()
    cy.contains('Django Admin').click()
    cy.contains('Adresy e-mail').click()
    cy.contains(email).click()
    cy.contains('Zweryfikowany').click()
    cy.contains('Zapisz').click()
    cy.contains('Wyloguj').click()
    cy.contains('Wylogowany')
  })

  it('log in and log out as existing user', () => {
		cy.visit('/')
    cy.contains('Zaloguj').click()
    cy.get('#id_login')
      .type(userName)
      .should('have.value', userName)
    cy.get('#id_password')
      .type(userPassword)
      .should('have.value', userPassword)
    cy.get('.primaryAction').click()
    cy.contains('Zalogowano jako')

    // FIXME add here tests using logged in user

    cy.visit('/isap/')
    cy.contains("Wyloguj").click()
    cy.contains("Czy na pewno wylogować?")
    cy.get('.btn-danger').click()
    cy.contains("Zaloguj")
  })

  it('remove existing user using test-admin account', () => {
    cy.visit('/')
    cy.contains('Zaloguj').click()
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
    cy.contains('Tak, na pewno').click()
    cy.contains('Wyloguj').click()
    cy.visit('/')
  })
})
